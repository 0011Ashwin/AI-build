#!/bin/bash

# Justice AI Workflow Deployment Script
# Deploys to Google Cloud Run

set -euo pipefail

# Configuration
PROJECT_ID=${1:-"justice-ai-project"}
REGION=${2:-"us-central1"}
REPOSITORY="justice-ai-repository"
IMAGE_REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}"

retry_push() {
    local image_name="$1"
    local max_attempts=4
    local attempt=1

    while [ "$attempt" -le "$max_attempts" ]; do
        echo "Pushing image (attempt ${attempt}/${max_attempts}): ${image_name}"
        if docker push "${image_name}"; then
            return 0
        fi

        if [ "$attempt" -lt "$max_attempts" ]; then
            local sleep_seconds=$((attempt * 5))
            echo "Push failed, retrying in ${sleep_seconds}s..."
            sleep "$sleep_seconds"
        fi

        attempt=$((attempt + 1))
    done

    return 1
}

publish_image() {
    local agent_name="$1"
    local source_dir="$2"
    local image_name="$3"

    echo "Building $agent_name..."

    # Try local Docker first for speed, then fall back to Cloud Build when network push fails.
    if command -v docker >/dev/null 2>&1; then
        if docker build -t "${image_name}" "${source_dir}"; then
            echo "Pushing $agent_name to Artifact Registry..."
            if retry_push "${image_name}"; then
                return 0
            fi

            echo "Local push failed for $agent_name. Falling back to Cloud Build..."
        else
            echo "Local Docker build failed for $agent_name. Falling back to Cloud Build..."
        fi
    else
        echo "Docker not available. Using Cloud Build for $agent_name..."
    fi

    echo "Submitting $agent_name build to Cloud Build..."
    gcloud builds submit "${source_dir}" --tag "${image_name}" --project "${PROJECT_ID}"
}

echo "🚀 Justice AI Workflow Deployment"
echo "=================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Artifact Registry: $IMAGE_REGISTRY"
echo ""

# Set Google Cloud project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📡 Enabling Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com

# Ensure Artifact Registry repository exists
echo "📦 Setting up Artifact Registry repository..."
if ! gcloud artifacts repositories describe "$REPOSITORY" --location "$REGION" >/dev/null 2>&1; then
    gcloud artifacts repositories create "$REPOSITORY" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Justice AI Workflow container images"
fi

# Configure Docker auth for Artifact Registry
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Build and push Docker images
echo "🏗️  Building Docker images..."

AGENTS=("chief_justice" "quantitative_auditor" "legal_researcher" "mitigator_juror" "strict_auditor_juror" "ethicist_juror" "app")

for agent in "${AGENTS[@]}"
do
    IMAGE_NAME="${IMAGE_REGISTRY}/${agent}:latest"

    if [ "$agent" == "app" ]; then
        publish_image "$agent" "./app" "${IMAGE_NAME}"
    else
        publish_image "$agent" "./agents/${agent}" "${IMAGE_NAME}"
    fi
done

# Deploy to Cloud Run
echo "☁️  Deploying to Google Cloud Run..."

for agent in "${AGENTS[@]}"
do
    SERVICE_NAME="${agent//_/-}"
    if [ "$agent" == "app" ]; then
        SERVICE_NAME="justice-ai-app"
    fi

    echo "Deploying $SERVICE_NAME from $agent image..."
    gcloud run deploy "${SERVICE_NAME}" \
        --image "${IMAGE_REGISTRY}/${agent}:latest" \
        --platform managed \
        --region "$REGION" \
        --memory 2Gi \
        --cpu 2 \
        --timeout 3600 \
        --set-env-vars "PROJECT_ID=$PROJECT_ID,REGION=$REGION" \
        --allow-unauthenticated
done

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service URLs:"
echo "- App: https://app-<random>.${REGION}.run.app"
echo "- Chief Justice: https://chief-justice-<random>.${REGION}.run.app"
echo "- Other agents deployed similarly"
echo ""
echo "To view logs:"
echo "  gcloud run logs read <service-name> --region $REGION --limit 50"

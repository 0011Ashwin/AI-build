#!/bin/bash

# Justice AI Workflow Deployment Script
# Deploys to Google Cloud Run

set -e

# Configuration
PROJECT_ID=${1:-"justice-ai-project"}
REGION=${2:-"us-central1"}
IMAGE_REGISTRY="gcr.io"

echo "🚀 Justice AI Workflow Deployment"
echo "=================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set Google Cloud project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📡 Enabling Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    containerregistry.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com

# Build and push Docker images
echo "🏗️  Building Docker images..."

AGENTS=("chief_justice" "quantitative_auditor" "legal_researcher" "mitigator_juror" "strict_auditor_juror" "ethicist_juror" "app")

for agent in "${AGENTS[@]}"
do
    echo "Building $agent..."
    if [ "$agent" == "app" ]; then
        docker build -t ${IMAGE_REGISTRY}/${PROJECT_ID}/${agent}:latest ./app
    else
        docker build -t ${IMAGE_REGISTRY}/${PROJECT_ID}/${agent}:latest ./agents/${agent}
    fi
    
    echo "Pushing $agent to Google Container Registry..."
    docker push ${IMAGE_REGISTRY}/${PROJECT_ID}/${agent}:latest
done

# Deploy to Cloud Run
echo "☁️  Deploying to Google Cloud Run..."

for agent in "${AGENTS[@]}"
do
    echo "Deploying $agent..."
    gcloud run deploy ${agent} \
        --image ${IMAGE_REGISTRY}/${PROJECT_ID}/${agent}:latest \
        --platform managed \
        --region $REGION \
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

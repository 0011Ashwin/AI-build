#!/bin/bash

# ============================================================================
# PHASE 3: Deploy Agents One-by-One
# ============================================================================
# This script deploys each agent individually to Google Cloud Run
# Run this THIRD after setting up database
# Usage: ./deploy-03-deploy-agents.sh --project-id <PROJECT_ID> [--region us-central1]

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID=""
REGION="us-central1"
SERVICE_ACCOUNT_NAME="justice-ai-sa"
VERBOSE=false
DEPLOY_AGENT="all"

# ============================================================================
# PARSING ARGUMENTS
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --agent)
            DEPLOY_AGENT="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ============================================================================
# VALIDATION
# ============================================================================

if [ -z "$PROJECT_ID" ]; then
    echo "Error: --project-id is required"
    echo "Usage: ./deploy-03-deploy-agents.sh --project-id <PROJECT_ID>"
    exit 1
fi

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
REGISTRY_REPO="justice-ai-repository"
REGISTRY_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_REPO"

declare -a AGENTS=(
    "chief-justice:./agents/chief_justice"
    "quantitative-auditor:./agents/quantitative_auditor"
    "legal-researcher:./agents/legal_researcher"
    "mitigator-juror:./agents/mitigator_juror"
    "strict-auditor-juror:./agents/strict_auditor_juror"
    "ethicist-juror:./agents/ethicist_juror"
)

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

write_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║  PHASE 3: DEPLOY AGENTS ONE-BY-ONE                                ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
}

write_section() {
    local title="$1"
    echo ""
    echo "┌──────────────────────────────────────────────────────────────────┐"
    echo "│ $title"
    echo "└──────────────────────────────────────────────────────────────────┘"
}

write_subsection() {
    local title="$1"
    echo ""
    echo "  ▶ $title"
}

write_success() {
    echo "✓ $1"
}

write_warning() {
    echo "⚠ $1"
}

write_info() {
    echo "ℹ $1"
}

write_error() {
    echo "✗ ERROR: $1"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

write_header

# Prerequisites Check
write_section "Prerequisites Check"

if ! command -v gcloud &> /dev/null; then
    write_error "Google Cloud SDK (gcloud) not found"
    exit 1
fi
write_success "Google Cloud SDK found"

if ! command -v docker &> /dev/null; then
    write_error "Docker not found. Please install Docker"
    exit 1
fi
write_success "Docker found"

# Set project
write_info "Setting project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID" > /dev/null 2>&1
write_success "Project configured"

# ============================================================================
# CREATE SERVICE ACCOUNT (if needed)
# ============================================================================

write_section "Setting Up Service Account"

write_info "Checking if service account exists..."

if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" > /dev/null 2>&1; then
    write_warning "Service account already exists"
else
    write_info "Creating service account: $SERVICE_ACCOUNT_NAME"
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" --project="$PROJECT_ID" > /dev/null 2>&1
    write_success "Service account created"
    sleep 2
fi

# Assign roles
write_info "Assigning required IAM roles..."
ROLES=(
    "roles/aiplatform.user"
    "roles/storage.objectViewer"
    "roles/firestore.viewer"
    "roles/logging.logWriter"
)

for role in "${ROLES[@]}"; do
    printf "  Assigning %s... " "$role"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" \
        --quiet > /dev/null 2>&1
    echo "✓"
done

write_success "Service account configured with required roles"

# ============================================================================
# SETUP ARTIFACT REGISTRY
# ============================================================================

write_section "Setting Up Artifact Registry"

write_info "Checking if Artifact Registry repository exists..."

if gcloud artifacts repositories describe "$REGISTRY_REPO" --location="$REGION" --project="$PROJECT_ID" > /dev/null 2>&1; then
    write_warning "Artifact Registry repository already exists"
else
    write_info "Creating Artifact Registry repository: $REGISTRY_REPO"
    gcloud artifacts repositories create "$REGISTRY_REPO" \
        --repository-format=docker \
        --location="$REGION" \
        --project="$PROJECT_ID" > /dev/null 2>&1
    write_success "Artifact Registry repository created"
    sleep 2
fi

write_info "Configuring Docker authentication..."
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet > /dev/null 2>&1
write_success "Docker authentication configured"

# ============================================================================
# BUILD DOCKER IMAGES
# ============================================================================

write_section "Building Agent Docker Images"

TOTAL_AGENTS=${#AGENTS[@]}
BUILT_COUNT=0

for agent_config in "${AGENTS[@]}"; do
    BUILT_COUNT=$((BUILT_COUNT + 1))
    
    IFS=':' read -r agent_name agent_path <<< "$agent_config"
    
    write_subsection "[$BUILT_COUNT/$TOTAL_AGENTS] Building $agent_name"
    
    IMAGE_NAME="$REGISTRY_URL/$agent_name:latest"
    write_info "Image: $IMAGE_NAME"
    
    if docker build -t "$IMAGE_NAME" -f "$agent_path/Dockerfile" "$agent_path" > /dev/null 2>&1; then
        write_success "Image built successfully"
    else
        write_error "Failed to build image for $agent_name"
        exit 1
    fi
done

write_success "All agent images built successfully"

# ============================================================================
# PUSH IMAGES TO ARTIFACT REGISTRY
# ============================================================================

write_section "Pushing Images to Artifact Registry"

PUSH_COUNT=0
for agent_config in "${AGENTS[@]}"; do
    PUSH_COUNT=$((PUSH_COUNT + 1))
    
    IFS=':' read -r agent_name agent_path <<< "$agent_config"
    
    write_subsection "[$PUSH_COUNT/$TOTAL_AGENTS] Pushing $agent_name"
    
    IMAGE_NAME="$REGISTRY_URL/$agent_name:latest"
    write_info "Image: $IMAGE_NAME"
    
    if docker push "$IMAGE_NAME" > /dev/null 2>&1; then
        write_success "Image pushed successfully"
    else
        write_error "Failed to push image for $agent_name"
        exit 1
    fi
done

write_success "All agent images pushed to Artifact Registry"

# ============================================================================
# DEPLOY AGENTS TO CLOUD RUN
# ============================================================================

write_section "Deploying Agents to Cloud Run"

write_info "Cloud Run Configuration:"
write_info "  Memory: 2Gi"
write_info "  CPU: 2"
write_info "  Timeout: 3600s"
write_info "  Max Concurrency: 80"
write_info ""

DEPLOY_COUNT=0
for agent_config in "${AGENTS[@]}"; do
    DEPLOY_COUNT=$((DEPLOY_COUNT + 1))
    
    IFS=':' read -r agent_name agent_path <<< "$agent_config"
    
    write_subsection "[$DEPLOY_COUNT/$TOTAL_AGENTS] Deploying $agent_name to Cloud Run"
    
    IMAGE_NAME="$REGISTRY_URL/$agent_name:latest"
    write_info "Service: $agent_name"
    write_info "Image: $IMAGE_NAME"
    
    write_info "  Starting deployment..."
    
    if gcloud run deploy "$agent_name" \
        --image="$IMAGE_NAME" \
        --platform=managed \
        --region="$REGION" \
        --allow-unauthenticated \
        --memory="2Gi" \
        --cpu="2" \
        --timeout="3600" \
        --concurrency="80" \
        --service-account="$SERVICE_ACCOUNT_EMAIL" \
        --project="$PROJECT_ID" \
        --quiet > /dev/null 2>&1; then
        
        write_success "Deployment completed"
        
        SERVICE_URL=$(gcloud run services describe "$agent_name" \
            --region="$REGION" \
            --format="value(status.url)" \
            --project="$PROJECT_ID" 2>/dev/null || echo "")
        
        if [ ! -z "$SERVICE_URL" ]; then
            write_info "Service URL: $SERVICE_URL"
        fi
        
        sleep 3
    else
        write_error "Failed to deploy $agent_name"
        exit 1
    fi
done

write_success "All agents deployed successfully"

# ============================================================================
# VERIFY DEPLOYMENTS
# ============================================================================

write_section "Verifying Agent Deployments"

write_info "Checking deployed services..."
write_info ""

VERIFY_COUNT=0
for agent_config in "${AGENTS[@]}"; do
    VERIFY_COUNT=$((VERIFY_COUNT + 1))
    IFS=':' read -r agent_name _ <<< "$agent_config"
    
    printf "  [%d/6] %s: " "$VERIFY_COUNT" "$agent_name"
    
    SERVICE_INFO=$(gcloud run services describe "$agent_name" \
        --region="$REGION" \
        --format="value(status.conditions[0].status)" \
        --project="$PROJECT_ID" 2>/dev/null || echo "")
    
    if [[ "$SERVICE_INFO" == *"True"* ]]; then
        echo "✓"
        
        SERVICE_URL=$(gcloud run services describe "$agent_name" \
            --region="$REGION" \
            --format="value(status.url)" \
            --project="$PROJECT_ID" 2>/dev/null || echo "")
        
        if [ ! -z "$SERVICE_URL" ]; then
            write_info "    URL: $SERVICE_URL"
        fi
    else
        echo "⏳ Initializing"
    fi
done

# ============================================================================
# COMPLETION
# ============================================================================

write_section "PHASE 3 Complete ✓"
write_info "All 6 agents deployed successfully to Cloud Run"
write_info ""
write_info "Deployed Agents:"
for agent_config in "${AGENTS[@]}"; do
    IFS=':' read -r agent_name _ <<< "$agent_config"
    write_info "  • $agent_name"
done
write_info ""
write_info "🎯 Next Step: Run deploy-04-deploy-app.sh"
write_info ""
write_info "   ./deploy-04-deploy-app.sh --project-id $PROJECT_ID --region $REGION"
write_info ""

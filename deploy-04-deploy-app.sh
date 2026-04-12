#!/bin/bash

# ============================================================================
# PHASE 4: Deploy Main Application
# ============================================================================
# This script deploys the main FastAPI application to Google Cloud Run
# Run this FOURTH after deploying all agents
# Usage: ./deploy-04-deploy-app.sh --project-id <PROJECT_ID> [--region us-central1]

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID=""
REGION="us-central1"
SERVICE_ACCOUNT_NAME="justice-ai-sa"
VERBOSE=false

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
    echo "Usage: ./deploy-04-deploy-app.sh --project-id <PROJECT_ID>"
    exit 1
fi

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
REGISTRY_REPO="justice-ai-repository"
REGISTRY_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_REPO"
APP_NAME="justice-ai-app"
APP_ROOT="./app"

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

write_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║  PHASE 4: DEPLOY MAIN APPLICATION                                 ║"
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
# BUILD MAIN APP DOCKER IMAGE
# ============================================================================

write_section "Building Main Application Image"

write_info "Building application Docker image..."
write_info "Image Root: $APP_ROOT"

IMAGE_NAME="$REGISTRY_URL/$APP_NAME:latest"
write_info "Docker Image: $IMAGE_NAME"
write_info ""

if docker build -t "$IMAGE_NAME" -f "$APP_ROOT/Dockerfile" "$APP_ROOT" > /dev/null 2>&1; then
    write_success "Application image built successfully"
else
    write_error "Failed to build main application image"
    exit 1
fi

# ============================================================================
# PUSH IMAGE TO ARTIFACT REGISTRY
# ============================================================================

write_section "Pushing Image to Artifact Registry"

write_info "Pushing application image to registry..."

if docker push "$IMAGE_NAME" > /dev/null 2>&1; then
    write_success "Application image pushed successfully"
else
    write_error "Failed to push application image"
    exit 1
fi

# ============================================================================
# DEPLOY APPLICATION TO CLOUD RUN
# ============================================================================

write_section "Deploying Application to Cloud Run"

write_info "Cloud Run Configuration:"
write_info "  Service Name: $APP_NAME"
write_info "  Memory: 4Gi"
write_info "  CPU: 4"
write_info "  Timeout: 3600s"
write_info "  Max Concurrency: 100"
write_info ""

write_info "Deploying service..."
write_info "Starting Cloud Run deployment (this may take 2-3 minutes)..."
write_info ""

if gcloud run deploy "$APP_NAME" \
    --image="$IMAGE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --allow-unauthenticated \
    --memory="4Gi" \
    --cpu="4" \
    --timeout="3600" \
    --concurrency="100" \
    --service-account="$SERVICE_ACCOUNT_EMAIL" \
    --project="$PROJECT_ID" \
    --quiet > /dev/null 2>&1; then
    
    write_success "Application deployment completed successfully"
else
    write_error "Failed to deploy main application"
    exit 1
fi

# ============================================================================
# GET APPLICATION URL
# ============================================================================

write_section "Application Details"

write_info "Retrieving application URL..."
APP_URL=$(gcloud run services describe "$APP_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID" 2>/dev/null || echo "")

if [ ! -z "$APP_URL" ]; then
    write_success "Application deployed successfully"
    write_info ""
    write_info "🌐 Application URL:"
    echo "    $APP_URL"
    write_info ""
else
    write_warning "Could not retrieve application URL (service may still be initializing)"
    write_info "Check Cloud Console: https://console.cloud.google.com/run?project=$PROJECT_ID"
fi

# ============================================================================
# VERIFY APPLICATION HEALTH
# ============================================================================

write_section "Verifying Application"

write_info "Waiting for application to initialize..."
sleep 10

if [ ! -z "$APP_URL" ]; then
    write_info "Testing health endpoint..."
    
    HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/health" 2>/dev/null || echo "000")
    
    if [ "$HEALTH_CHECK" = "200" ]; then
        write_success "Health check passed - Application is running"
        write_info "  Status Code: 200"
        write_info "  Response: OK"
    else
        write_warning "Unexpected health status: $HEALTH_CHECK"
    fi
else
    write_warning "Skipping health check (URL not available)"
fi

# ============================================================================
# DISPLAY NEXT STEPS
# ============================================================================

write_section "PHASE 4 Complete ✓"
write_info "Main application deployed successfully to Cloud Run"
write_info ""

if [ ! -z "$APP_URL" ]; then
    write_info "📊 Application Ready - Access it at:"
    echo "    $APP_URL"
    write_info ""
fi

write_info "✅ All deployment phases completed successfully!"
write_info ""
write_info "Deployment Summary:"
write_info "  ✓ APIs enabled (13 services)"
write_info "  ✓ Database configured (Firestore)"
write_info "  ✓ Agents deployed (6 services)"
write_info "  ✓ Application deployed (1 service)"
write_info ""

write_info "📈 Monitor and Manage:"
write_info "  Cloud Console: https://console.cloud.google.com/run?project=$PROJECT_ID"
write_info "  View Logs: gcloud logging read 'resource.type=cloud_run_revision' --project=$PROJECT_ID"
write_info "  View Metrics: https://console.cloud.google.com/monitoring?project=$PROJECT_ID"
write_info ""

write_success "🎉 Deployment Complete!"
write_info ""

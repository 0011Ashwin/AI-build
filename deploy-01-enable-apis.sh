#!/bin/bash

# ============================================================================
# PHASE 1: Enable Required Google Cloud APIs
# ============================================================================
# This script enables all 13 required GCP APIs for Justice AI Workflow
# Run this FIRST before any other deployment steps
# Usage: ./deploy-01-enable-apis.sh --project-id <PROJECT_ID>

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID=""
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
    echo "Usage: ./deploy-01-enable-apis.sh --project-id <PROJECT_ID>"
    exit 1
fi

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo "✗ ERROR: Google Cloud SDK (gcloud) not found"
    exit 1
fi

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

write_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║  PHASE 1: ENABLE GOOGLE CLOUD APIs                               ║"
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
    local message="$1"
    echo "✓ $message"
}

write_warning() {
    local message="$1"
    echo "⚠ $message"
}

write_info() {
    local message="$1"
    echo "ℹ $message"
}

write_error() {
    local message="$1"
    echo "✗ ERROR: $message"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

write_header

# Prerequisites Check
write_section "Prerequisites Check"

write_info "Checking Google Cloud SDK..."
GCLOUD_VERSION=$(gcloud --version | head -1)
write_success "Google Cloud SDK found: $GCLOUD_VERSION"

# Set project
write_section "Setting GCP Project"
write_info "Setting project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID" > /dev/null 2>&1
write_success "Project set to: $PROJECT_ID"

# ============================================================================
# ENABLE REQUIRED APIs
# ============================================================================

write_section "Enabling Required Google Cloud APIs"

declare -a APIS=(
    "aiplatform.googleapis.com"
    "run.googleapis.com"
    "storage-api.googleapis.com"
    "firestore.googleapis.com"
    "logging.googleapis.com"
    "monitoring.googleapis.com"
    "artifactregistry.googleapis.com"
    "cloudbuild.googleapis.com"
    "secretmanager.googleapis.com"
    "container.googleapis.com"
    "compute.googleapis.com"
    "servicenetworking.googleapis.com"
    "cloudresourcemanager.googleapis.com"
)

TOTAL_APIS=${#APIS[@]}
ENABLED_COUNT=0

write_info "Total APIs to enable: $TOTAL_APIS"
write_info ""

for api in "${APIS[@]}"; do
    ENABLED_COUNT=$((ENABLED_COUNT + 1))
    display_name="${api%.googleapis.com}"
    
    printf "  [%d/%d] Enabling %-40s " "$ENABLED_COUNT" "$TOTAL_APIS" "$display_name..."
    
    if gcloud services enable "$api" --project="$PROJECT_ID" > /dev/null 2>&1; then
        echo "✓"
    else
        # Check if already enabled
        if gcloud services list --enabled --project="$PROJECT_ID" 2>/dev/null | grep -q "$api"; then
            echo "(already enabled)"
        else
            echo "✗"
            write_error "Failed to enable $api"
            exit 1
        fi
    fi
done

# ============================================================================
# VERIFICATION
# ============================================================================

write_section "Verifying Enabled APIs"

write_info "Verifying all APIs are enabled..."
ENABLED_APIS=$(gcloud services list --enabled --project="$PROJECT_ID" --format="value(name)" 2>/dev/null || echo "")

for api in "${APIS[@]}"; do
    if echo "$ENABLED_APIS" | grep -q "$api"; then
        display_name="${api%.googleapis.com}"
        write_success "$display_name is enabled"
    fi
done

# ============================================================================
# COMPLETION
# ============================================================================

write_section "PHASE 1 Complete ✓"
write_info "All 13 required APIs have been enabled"
write_info ""
write_info "🎯 Next Step: Run deploy-02-setup-database.sh"
write_info ""
write_info "   ./deploy-02-setup-database.sh --project-id $PROJECT_ID"
write_info ""

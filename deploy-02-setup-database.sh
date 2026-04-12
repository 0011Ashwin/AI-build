#!/bin/bash

# ============================================================================
# PHASE 2: Setup Database & Storage
# ============================================================================
# This script sets up Firestore database and Cloud Storage buckets
# Run this SECOND after enabling APIs
# Usage: ./deploy-02-setup-database.sh --project-id <PROJECT_ID> [--region us-central1]

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID=""
REGION="us-central1"
SETUP_FIRESTORE=true
CREATE_BUCKETS=true
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
    echo "Usage: ./deploy-02-setup-database.sh --project-id <PROJECT_ID>"
    exit 1
fi

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

write_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║  PHASE 2: SETUP DATABASE & STORAGE                                ║"
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

write_info "Checking Google Cloud SDK..."
if ! command -v gcloud &> /dev/null; then
    write_error "Google Cloud SDK (gcloud) not found"
    exit 1
fi
write_success "Google Cloud SDK found"

# Set project
write_section "Setting GCP Project"
write_info "Setting project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID" > /dev/null 2>&1
write_success "Project set to: $PROJECT_ID"

# ============================================================================
# SETUP FIRESTORE DATABASE
# ============================================================================

if [ "$SETUP_FIRESTORE" = true ]; then
    write_section "Setting Up Firestore Database"
    
    write_info "Checking if Firestore database already exists..."
    
    if gcloud firestore databases describe --project="$PROJECT_ID" > /dev/null 2>&1; then
        write_warning "Firestore database already exists"
        write_info "Skipping database creation"
    else
        write_info "Creating Firestore database in $REGION (Native mode)..."
        
        if gcloud firestore databases create --project="$PROJECT_ID" --location="$REGION" --type=firestore-native > /dev/null 2>&1; then
            write_success "Firestore database created successfully"
            write_info "Location: $REGION | Mode: Native"
            
            write_info "Waiting for database to initialize (this takes ~30-60 seconds)..."
            sleep 5
        else
            write_error "Failed to create Firestore database"
            exit 1
        fi
    fi
fi

# ============================================================================
# INITIALIZE FIRESTORE COLLECTIONS
# ============================================================================

write_section "Initializing Firestore Collections"

write_info "Firestore collections to initialize:"
write_info "  - cases: Audit cases and submissions"
write_info "  - audits: Audit analysis results"
write_info "  - legal_precedents: Legal precedent RAG data"
write_info "  - case_verdicts: Agent jury verdicts"
write_info "  - metrics: System performance metrics"

write_info ""
write_warning "Note: Firestore collections are created automatically when first data is written"
write_success "Collections configuration ready"

# ============================================================================
# CREATE CLOUD STORAGE BUCKETS
# ============================================================================

if [ "$CREATE_BUCKETS" = true ]; then
    write_section "Creating Cloud Storage Buckets"
    
    BUCKET_COUNT=0
    BUCKETS=(
        "justice-ai-cases-$PROJECT_ID"
        "justice-ai-reports-$PROJECT_ID"
        "justice-ai-legal-docs-$PROJECT_ID"
    )
    
    write_info "Total buckets to create: ${#BUCKETS[@]}"
    write_info ""
    
    for bucket in "${BUCKETS[@]}"; do
        BUCKET_COUNT=$((BUCKET_COUNT + 1))
        printf "  [%d/3] Creating %-50s " "$BUCKET_COUNT" "$bucket..."
        
        if gcloud storage buckets describe "gs://$bucket" --project="$PROJECT_ID" > /dev/null 2>&1; then
            echo "(already exists)"
        else
            if gcloud storage buckets create "gs://$bucket" --location="$REGION" --project="$PROJECT_ID" > /dev/null 2>&1; then
                echo "✓"
            else
                echo "✗"
                write_error "Failed to create bucket $bucket"
                exit 1
            fi
        fi
    done
    
    write_info ""
    write_success "Cloud Storage buckets created/verified"
fi

# ============================================================================
# VERIFY STORAGE SETUP
# ============================================================================

write_section "Verifying Storage Setup"

write_info "Firestore database status:"
if gcloud firestore databases describe --project="$PROJECT_ID" > /dev/null 2>&1; then
    write_success "Firestore database is ready"
else
    write_warning "Could not verify Firestore status (may still be initializing)"
fi

write_info ""
write_info "Cloud Storage buckets:"
BUCKETS_LIST=$(gcloud storage buckets list --project="$PROJECT_ID" --filter="name:justice-ai*" --format="value(name)" 2>/dev/null || echo "")

if [ ! -z "$BUCKETS_LIST" ]; then
    while IFS= read -r bucket; do
        if [ ! -z "$bucket" ]; then
            write_success "Bucket: $bucket"
        fi
    done <<< "$BUCKETS_LIST"
else
    write_warning "Could not list buckets (may still be initializing)"
fi

# ============================================================================
# COMPLETION
# ============================================================================

write_section "PHASE 2 Complete ✓"
write_info "Database and storage infrastructure is ready"
write_info ""
write_info "🎯 Next Step: Run deploy-03-deploy-agents.sh"
write_info ""
write_info "   ./deploy-03-deploy-agents.sh --project-id $PROJECT_ID --region $REGION"
write_info ""

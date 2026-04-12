#!/bin/bash

# ============================================================================
# MASTER DEPLOYMENT ORCHESTRATOR (Bash Version)
# ============================================================================
# This script orchestrates the step-by-step deployment of Justice AI Workflow
# Can run all phases sequentially or deploy specific phases
# Works in Google Cloud Shell
# Usage: ./deploy-master.sh --project-id <PROJECT_ID> [--phase all|apis|database|agents|app]

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID=""
REGION="us-central1"
PHASE="all"
SKIP_CONFIRMATION=false
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
        --phase)
            PHASE="$2"
            shift 2
            ;;
        --skip-confirmation)
            SKIP_CONFIRMATION=true
            shift
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
    echo ""
    echo "Usage: ./deploy-master.sh --project-id <PROJECT_ID> [options]"
    echo ""
    echo "Options:"
    echo "  --region              Google Cloud Region (default: us-central1)"
    echo "  --phase               Phase to run: all, apis, database, agents, app (default: all)"
    echo "  --skip-confirmation   Skip confirmation prompts"
    echo "  --verbose             Enable verbose logging"
    exit 1
fi

# Validate phase
case "$PHASE" in
    all|apis|database|agents|app)
        ;;
    *)
        echo "Error: Invalid phase '$PHASE'"
        echo "Valid phases: all, apis, database, agents, app"
        exit 1
        ;;
esac

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

write_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                 JUSTICE AI WORKFLOW                               ║"
    echo "║             MASTER DEPLOYMENT ORCHESTRATOR                        ║"
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

# Display Configuration
write_section "Deployment Configuration"
write_info "Project ID: $PROJECT_ID"
write_info "Region: $REGION"
write_info "Phase: $PHASE"
write_info ""

# Determine phases to run
declare -a PHASES_TO_RUN
case "$PHASE" in
    all)
        PHASES_TO_RUN=("apis" "database" "agents" "app")
        ;;
    *)
        PHASES_TO_RUN=("$PHASE")
        ;;
esac

# Display deployment plan
write_section "Deployment Plan"
write_info "Phases to execute:"

PHASE_NAMES=(
    "apis:Enable Google Cloud APIs"
    "database:Setup Database & Storage"
    "agents:Deploy Agents"
    "app:Deploy Main Application"
)

for phase_to_run in "${PHASES_TO_RUN[@]}"; do
    for phase_info in "${PHASE_NAMES[@]}"; do
        IFS=':' read -r phase_key phase_name <<< "$phase_info"
        if [ "$phase_key" = "$phase_to_run" ]; then
            idx=$((idx + 1))
            write_info "  PHASE $idx - $phase_name"
        fi
    done
done
write_info ""

# Confirmation
if [ "$SKIP_CONFIRMATION" = false ]; then
    write_warning "This will deploy to Google Cloud Platform"
    read -p "Continue with deployment? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        write_info "Deployment cancelled"
        exit 0
    fi
fi

# ============================================================================
# EXECUTE PHASES
# ============================================================================

TOTAL_PHASES=${#PHASES_TO_RUN[@]}
COMPLETED_PHASES=0
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for phase_name in "${PHASES_TO_RUN[@]}"; do
    COMPLETED_PHASES=$((COMPLETED_PHASES + 1))
    
    # Map phase to script
    case "$phase_name" in
        apis)
            SCRIPT_FILE="$SCRIPT_DIR/deploy-01-enable-apis.sh"
            PHASE_TITLE="PHASE 1: Enable APIs"
            ;;
        database)
            SCRIPT_FILE="$SCRIPT_DIR/deploy-02-setup-database.sh"
            PHASE_TITLE="PHASE 2: Setup Database"
            ;;
        agents)
            SCRIPT_FILE="$SCRIPT_DIR/deploy-03-deploy-agents.sh"
            PHASE_TITLE="PHASE 3: Deploy Agents"
            ;;
        app)
            SCRIPT_FILE="$SCRIPT_DIR/deploy-04-deploy-app.sh"
            PHASE_TITLE="PHASE 4: Deploy App"
            ;;
    esac
    
    write_section "EXECUTING: $PHASE_TITLE [$COMPLETED_PHASES/$TOTAL_PHASES]"
    
    if [ ! -f "$SCRIPT_FILE" ]; then
        write_error "Script not found: $SCRIPT_FILE"
        exit 1
    fi
    
    write_info "Running: $SCRIPT_FILE"
    write_info ""
    
    # Build parameters
    PARAMS="--project-id $PROJECT_ID"
    
    if [ "$phase_name" != "apis" ]; then
        PARAMS="$PARAMS --region $REGION"
    fi
    
    if [ "$VERBOSE" = true ]; then
        PARAMS="$PARAMS --verbose"
    fi
    
    # Execute phase script
    if bash "$SCRIPT_FILE" $PARAMS; then
        :
    else
        write_error "Phase execution failed"
        exit 1
    fi
    
    # Wait between phases
    if [ $COMPLETED_PHASES -lt $TOTAL_PHASES ]; then
        write_info ""
        write_info "Preparing next phase..."
        sleep 3
    fi
done

# ============================================================================
# FINAL SUMMARY
# ============================================================================

write_section "DEPLOYMENT COMPLETE ✓"

write_info ""
write_info "🎉 All phases executed successfully!"
write_info ""

write_success "Summary:"
write_info "  ✓ Phase 1: APIs Enabled (13 services)"
write_info "  ✓ Phase 2: Database Configured (Firestore + Storage)"
write_info "  ✓ Phase 3: Agents Deployed (6 services)"
write_info "  ✓ Phase 4: Application Deployed (1 service)"
write_info ""

write_info "📊 Next Steps:"
write_info "  1. Access your application in Cloud Console"
write_info "     https://console.cloud.google.com/run?project=$PROJECT_ID"
write_info ""
write_info "  2. View application logs"
write_info "     gcloud logging read --limit 100 --project=$PROJECT_ID"
write_info ""
write_info "  3. Get service endpoints"
write_info "     gcloud run services list --project=$PROJECT_ID"
write_info ""

write_info "📈 Monitoring:"
write_info "  • Cloud Console: https://console.cloud.google.com?project=$PROJECT_ID"
write_info "  • Logs: https://console.cloud.google.com/logs?project=$PROJECT_ID"
write_info "  • Monitoring: https://console.cloud.google.com/monitoring?project=$PROJECT_ID"
write_info ""

write_success "Deployment Ready!"
write_info ""

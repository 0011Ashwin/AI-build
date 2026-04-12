# ============================================================================
# PHASE 1: Enable Required Google Cloud APIs
# ============================================================================
# This script enables all 13 required GCP APIs for Justice AI Workflow
# Run this FIRST before any other deployment steps

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="Google Cloud Project ID")]
    [string]$ProjectID
)

$ErrorActionPreference = "Stop"


# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

function Write-Header {
    Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  PHASE 1: ENABLE GOOGLE CLOUD APIs                               ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
}

function Write-Section {
    param([string]$Title)
    Write-Host "`n┌──────────────────────────────────────────────────────────────────┐" -ForegroundColor Blue
    Write-Host "│ $Title" -ForegroundColor Blue
    Write-Host "└──────────────────────────────────────────────────────────────────┘" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-FatalError {
    param([string]$Message)
    Write-Host "✗ ERROR: $Message" -ForegroundColor Red
    exit 1
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Header

# Check prerequisites
Write-Section "Prerequisites Check"

# Check gcloud
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-FatalError "Google Cloud SDK (gcloud) not found. Please install it from https://cloud.google.com/sdk/docs/install"
}
Write-Success "Google Cloud SDK found"

# Check authentication
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if ([string]::IsNullOrEmpty($authCheck)) {
    Write-FatalError "No active Google Cloud authentication found. Run: gcloud auth login"
}
Write-Success "Google Cloud authentication verified: $authCheck"

# Set project
Write-Section "Setting GCP Project"
Write-Info "Setting project to: $ProjectID"
$projectOutput = (gcloud config set project $ProjectID 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0) {
    Write-FatalError "Failed to set GCP project: $projectOutput"
}
Write-Success "Project set to: $ProjectID"

# ============================================================================
# ENABLE REQUIRED APIs
# ============================================================================

Write-Section "Enabling Required Google Cloud APIs"

$apis = @(
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "storage-api.googleapis.com",
    "firestore.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "container.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "cloudresourcemanager.googleapis.com"
)

$totalApis = $apis.Count
$enabledCount = 0

Write-Info "Total APIs to enable: $totalApis"
Write-Info ""

foreach ($api in $apis) {
    $enabledCount++
    $displayName = $api -replace '\.googleapis\.com$'
    Write-Host "  [$enabledCount/$totalApis] Enabling $displayName..." -NoNewline
    
    try {
        $output = (gcloud services enable $api --project=$ProjectID 2>&1 | Out-String).Trim()
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
        } else {
            if ($output -like "*already enabled*" -or $output -like "*API is already enabled*") {
                Write-Host " (already enabled)" -ForegroundColor Gray
            } else {
                Write-Host " ✗" -ForegroundColor Red
                Write-FatalError "Failed to enable $api"
            }
        }
    } catch {
        Write-Host " ✗" -ForegroundColor Red
        Write-FatalError "Error enabling $api``: $_"
    }
}

# ============================================================================
# VERIFICATION
# ============================================================================

Write-Section "Verifying Enabled APIs"

$enabledApisList = (gcloud services list --enabled --project=$ProjectID --format="value(name)" 2>&1 | Out-String).Trim()
$enabledApis = $enabledApisList -split "`n" | Where-Object { $_ -match 'googleapis\.com$' }

Write-Info "Verified APIs enabled:"
foreach ($api in $apis) {
    $apiName = $api -replace '\.googleapis\.com$'
    if ($enabledApis -like "*$api*") {
        Write-Success "$apiName is enabled"
    } else {
        Write-Warning "$apiName may not be enabled yet (still initializing)"
    }
}

# ============================================================================
# COMPLETION
# ============================================================================

Write-Section "PHASE 1 Complete ✓"
Write-Info "All 13 required APIs have been enabled"
Write-Info ""
Write-Info "🎯 Next Step: Run deploy-02-setup-database.ps1"
Write-Info ""
Write-Info "   .\deploy-02-setup-database.ps1 -ProjectID '$ProjectID'"
Write-Info ""

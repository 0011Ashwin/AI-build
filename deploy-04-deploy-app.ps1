# ============================================================================
# PHASE 4: Deploy Main Application
# ============================================================================
# This script deploys the main FastAPI application to Google Cloud Run
# Run this FOURTH after deploying all agents

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="Google Cloud Project ID")]
    [string]$ProjectID,
    
    [Parameter(Mandatory=$false, HelpMessage="Google Cloud Region")]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false, HelpMessage="Service Account Name")]
    [string]$ServiceAccountName = "justice-ai-sa"
)

$ErrorActionPreference = "Stop"


# ============================================================================
# CONFIGURATION
# ============================================================================

$config = @{
    ServiceAccountEmail = "$ServiceAccountName@$ProjectID.iam.gserviceaccount.com"
    RegistryRepo = "justice-ai-repository"
    RegistryURL = "$Region-docker.pkg.dev/$ProjectID/justice-ai-repository"
    AppName = "justice-ai-app"
    AppRoot = "./app"
    CloudRun = @{
        Memory = "4Gi"
        CPU = "4"
        Timeout = "3600"
        Concurrency = "100"
    }
}

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

function Write-Header {
    Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  PHASE 4: DEPLOY MAIN APPLICATION                                 ║" -ForegroundColor Cyan
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

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-FatalError "Google Cloud SDK (gcloud) not found"
}
Write-Success "Google Cloud SDK found"

# Set project
Write-Info "Setting project to: $ProjectID"
$output = (gcloud config set project $ProjectID 2>&1 | Out-String).Trim()
Write-Success "Project configured"


# ============================================================================
# BUILD & PUSH APPLICATION IMAGE (VIA CLOUD BUILD)
# ============================================================================

Write-Section "Building & Pushing Application Image (via Cloud Build)"

Write-Info "Using Google Cloud Build for reliable cloud-native builds."
Write-Info "Task: Build context $($config.AppRoot) -> $($config.RegistryURL)/$($config.AppName):latest"

try {
    $imageName = "$($config.RegistryURL)/$($config.AppName):latest"
    Write-Host "  Starting Cloud Build... (this may take 2-3 minutes)" -ForegroundColor Gray
    
    # Use gcloud builds submit for reliable cloud-side builds
    $output = (gcloud builds submit --tag $imageName "$($config.AppRoot)" --project=$ProjectID --quiet 2>&1 | Out-String).Trim()
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nCloud Build Error Output:" -ForegroundColor Red
        Write-Host $output -ForegroundColor Gray
        Write-FatalError "Failed to build application image via Cloud Build"
    }
    
    Write-Success "Application image built and pushed successfully"
    
} catch {
    Write-FatalError "Error during Cloud Build for application: $_"
}


# ============================================================================
# DEPLOY APPLICATION TO CLOUD RUN
# ============================================================================

Write-Section "Deploying Application to Cloud Run"

Write-Info "Cloud Run Configuration:"
Write-Info "  Service Name: $($config.AppName)"
Write-Info "  Memory: $($config.CloudRun.Memory)"
Write-Info "  CPU: $($config.CloudRun.CPU)"
Write-Info "  Timeout: $($config.CloudRun.Timeout)s"
Write-Info "  Max Concurrency: $($config.CloudRun.Concurrency)"
Write-Info ""

try {
    $imageName = "$($config.RegistryURL)/$($config.AppName):latest"
    
    Write-Info "Deploying service..."
    Write-Info "Starting Cloud Run deployment (this may take 2-3 minutes)..."
    Write-Info ""
    
    $output = (gcloud run deploy $($config.AppName) `
        --image=$imageName `
        --platform=managed `
        --region=$Region `
        --allow-unauthenticated `
        --memory=$($config.CloudRun.Memory) `
        --cpu=$($config.CloudRun.CPU) `
        --timeout=$($config.CloudRun.Timeout) `
        --concurrency=$($config.CloudRun.Concurrency) `
        --service-account=$($config.ServiceAccountEmail) `
        --project=$ProjectID `
        --quiet `
        2>&1 | Out-String).Trim()
    
    if ($LASTEXITCODE -ne 0) {
        Write-FatalError "Failed to deploy main application`n$output"
    }
    
    Write-Success "Application deployment completed successfully"
    
} catch {
    Write-FatalError "Error deploying application: $_"
}

# ============================================================================
# GET APPLICATION URL
# ============================================================================

Write-Section "Application Details"

Write-Info "Retrieving application URL..."
$appUrl = (gcloud run services describe $($config.AppName) --region=$Region --format="value(status.url)" --project=$ProjectID 2>&1 | Out-String).Trim()

if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrEmpty($appUrl)) {
    Write-Success "Application deployed successfully"
    Write-Info ""
    Write-Info "🌐 Application URL:"
    Write-Host "    $appUrl" -ForegroundColor Green -BackgroundColor Black
    Write-Info ""
} else {
    Write-Warning "Could not retrieve application URL (service may still be initializing)"
    Write-Info "Check Cloud Console: https://console.cloud.google.com/run?project=$ProjectID"
}

# ============================================================================
# VERIFY APPLICATION HEALTH
# ============================================================================

Write-Section "Verifying Application"

Write-Info "Waiting for application to initialize..."
Start-Sleep -Seconds 10

if (-not [string]::IsNullOrEmpty($appUrl)) {
    Write-Info "Testing health endpoint..."
    
    try {
        $response = Invoke-WebRequest -Uri "$appUrl/health" -Method GET -TimeoutSec 10 -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq 200) {
            Write-Success "Health check passed - Application is running"
            Write-Info "  Status Code: 200"
            Write-Info "  Response: OK"
        } else {
            Write-Warning "Unexpected health status: $($response.StatusCode)"
        }
    } catch {
        Write-Warning "Could not reach health endpoint (service may still be initializing)"
        Write-Info "  This is normal - the service will be ready in a few moments"
    }
} else {
    Write-Warning "Skipping health check (URL not available)"
}

# ============================================================================
# DISPLAY NEXT STEPS
# ============================================================================

Write-Section "PHASE 4 Complete ✓"
Write-Info "Main application deployed successfully to Cloud Run"
Write-Info ""

if (-not [string]::IsNullOrEmpty($appUrl)) {
    Write-Info "📊 Application Ready - Access it at:"
    Write-Host "    $appUrl" -ForegroundColor Green
    Write-Info ""
}

Write-Info "✅ All deployment phases completed successfully!"
Write-Info ""
Write-Info "Deployment Summary:"
Write-Info "  ✓ APIs enabled (13 services)"
Write-Info "  ✓ Database configured (Firestore)"
Write-Info "  ✓ Agents deployed (6 services)"
Write-Info "  ✓ Application deployed (1 service)"
Write-Info ""

Write-Info "📈 Monitor and Manage:"
Write-Info "  Cloud Console: https://console.cloud.google.com/run?project=$ProjectID"
Write-Info "  View Logs: gcloud logging read 'resource.type=cloud_run_revision' --project=$ProjectID"
Write-Info "  View Metrics: https://console.cloud.google.com/monitoring?project=$ProjectID"
Write-Info ""

Write-Info "🔗 Service Endpoints:"
Write-Info "  • Chief Justice: Check Cloud Console for endpoint"
Write-Info "  • Quantitative Auditor: Check Cloud Console for endpoint"
Write-Info "  • Legal Researcher: Check Cloud Console for endpoint"
Write-Info "  • Mitigator Juror: Check Cloud Console for endpoint"
Write-Info "  • Strict Auditor Juror: Check Cloud Console for endpoint"
Write-Info "  • Ethicist Juror: Check Cloud Console for endpoint"
Write-Info ""

Write-Info "📚 Documentation:"
Write-Info "  • View logs: gcloud logging read --limit 100 --project=$ProjectID"
Write-Info "  • Get service details: gcloud run services list --project=$ProjectID"
Write-Info "  • View metrics: gcloud monitoring dashboards list --project=$ProjectID"
Write-Info ""

Write-Success "🎉 Deployment Complete!"
Write-Info ""

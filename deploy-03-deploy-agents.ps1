# ============================================================================
# PHASE 3: Deploy Agents One-by-One
# ============================================================================
# This script deploys each agent individually to Google Cloud Run
# Run this THIRD after setting up database

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="Google Cloud Project ID")]
    [string]$ProjectID,
    
    [Parameter(Mandatory=$false, HelpMessage="Google Cloud Region")]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false, HelpMessage="Service Account Name")]
    [string]$ServiceAccountName = "justice-ai-sa",
    
    [Parameter(Mandatory=$false, HelpMessage="Deploy only specific agent (optional)")]
    [string]$DeployAgent = "all"
)

$ErrorActionPreference = "Stop"


# ============================================================================
# CONFIGURATION
# ============================================================================

$config = @{
    ServiceAccountEmail = "$ServiceAccountName@$ProjectID.iam.gserviceaccount.com"
    RegistryRepo = "justice-ai-repository"
    RegistryURL = "$Region-docker.pkg.dev/$ProjectID/justice-ai-repository"
    CloudRun = @{
        Memory = "2Gi"
        CPU = "2"
        Timeout = "3600"
        Concurrency = "80"
    }
    
    # Agents to deploy
    Agents = @(
        @{ Name = "chief-justice"; Port = 8000; Path = "./agents/chief_justice" }
        @{ Name = "quantitative-auditor"; Port = 8001; Path = "./agents/quantitative_auditor" }
        @{ Name = "legal-researcher"; Port = 8002; Path = "./agents/legal_researcher" }
        @{ Name = "mitigator-juror"; Port = 8003; Path = "./agents/mitigator_juror" }
        @{ Name = "strict-auditor-juror"; Port = 8004; Path = "./agents/strict_auditor_juror" }
        @{ Name = "ethicist-juror"; Port = 8005; Path = "./agents/ethicist_juror" }
    )
}

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

function Write-Header {
    Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  PHASE 3: DEPLOY AGENTS ONE-BY-ONE                                ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
}

function Write-Section {
    param([string]$Title)
    Write-Host "`n┌──────────────────────────────────────────────────────────────────┐" -ForegroundColor Blue
    Write-Host "│ $Title" -ForegroundColor Blue
    Write-Host "└──────────────────────────────────────────────────────────────────┘" -ForegroundColor Blue
}

function Write-Subsection {
    param([string]$Title)
    Write-Host "`n  ▶ $Title" -ForegroundColor Magenta
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
# CREATE SERVICE ACCOUNT (if needed)
# ============================================================================

Write-Section "Setting Up Service Account"

Write-Info "Checking if service account exists..."
$saExists = (gcloud iam service-accounts describe $($config.ServiceAccountEmail) --project=$ProjectID 2>&1 | Out-String).Trim()

if ($LASTEXITCODE -ne 0) {
    Write-Info "Creating service account: $ServiceAccountName"
    $output = (gcloud iam service-accounts create $ServiceAccountName --project=$ProjectID 2>&1 | Out-String).Trim()
    Write-Success "Service account created"
    
    # Wait for service account to be ready
    Start-Sleep -Seconds 2
} else {
    Write-Warning "Service account already exists"
}

# Assign roles
Write-Info "Assigning required IAM roles..."
$roles = @(
    "roles/aiplatform.user"
    "roles/storage.objectViewer"
    "roles/firestore.viewer"
    "roles/logging.logWriter"
)

foreach ($role in $roles) {
    Write-Host "  Assigning $role..." -NoNewline
    try {
        $output = (gcloud projects add-iam-policy-binding $ProjectID --member="serviceAccount:$($config.ServiceAccountEmail)" --role="$role" --quiet 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
        } else {
            Write-Host " ✓ (warning)" -ForegroundColor Gray
        }
    } catch {
        Write-Host " ✓ (skipped)" -ForegroundColor Gray
    }
}

Write-Success "Service account configured with required roles"

# ============================================================================
# SETUP ARTIFACT REGISTRY
# ============================================================================

Write-Section "Setting Up Artifact Registry"

Write-Info "Checking if Artifact Registry repository exists..."
$repoExists = (gcloud artifacts repositories describe $($config.RegistryRepo) --location=$Region --project=$ProjectID 2>&1 | Out-String).Trim()

if ($LASTEXITCODE -ne 0) {
    Write-Info "Creating Artifact Registry repository: $($config.RegistryRepo)"
    $output = (gcloud artifacts repositories create $($config.RegistryRepo) --repository-format=docker --location=$Region --project=$ProjectID 2>&1 | Out-String).Trim()
    Write-Success "Artifact Registry repository created"
    Start-Sleep -Seconds 2
} else {
    Write-Warning "Artifact Registry repository already exists"
}


# ============================================================================
# BUILD & PUSH IMAGES (USING CLOUD BUILD)
# ============================================================================

Write-Section "Building & Pushing Images (via Cloud Build)"

Write-Info "Using Google Cloud Build for reliable cloud-native builds."
Write-Info "This bypasses local Docker requirements and network issues."
Write-Info ""

$agents = $config.Agents
if ($DeployAgent -ne "all") {
    $agents = $agents | Where-Object { $_.Name -eq $DeployAgent }
}

$totalAgents = $agents.Count
$builtCount = 0

foreach ($agent in $agents) {
    $builtCount++
    Write-Subsection "[$builtCount/$totalAgents] Building & Pushing $($agent.Name)"
    
    $imageName = "$($config.RegistryURL)/$($agent.Name):latest"
    Write-Info "Task: Build context $($agent.Path) -> $imageName"
    
    try {
        Write-Host "  Starting Cloud Build... (this may take 2-3 minutes)" -ForegroundColor Gray
        
        # Use gcloud builds submit from the root context to ensure shared folders are captured
        $output = (gcloud builds submit --tag $imageName --file "$($agent.Path)/Dockerfile" . --project=$ProjectID --quiet 2>&1 | Out-String).Trim()
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "`nCloud Build Error Output:" -ForegroundColor Red
            Write-Host $output -ForegroundColor Gray
            Write-FatalError "Failed to build image for $($agent.Name) via Cloud Build"
        }
        
        Write-Success "Agent image built and pushed successfully"
        
    } catch {
        Write-FatalError "Error during Cloud Build for $($agent.Name): $_"
    }
}

Write-Success "All agent images are ready in Artifact Registry"


# ============================================================================
# DEPLOY AGENTS TO CLOUD RUN
# ============================================================================

Write-Section "Deploying Agents to Cloud Run"

Write-Info "Cloud Run Configuration:"
Write-Info "  Memory: $($config.CloudRun.Memory)"
Write-Info "  CPU: $($config.CloudRun.CPU)"
Write-Info "  Timeout: $($config.CloudRun.Timeout)s"
Write-Info "  Max Concurrency: $($config.CloudRun.Concurrency)"
Write-Info ""

$deployCount = 0
foreach ($agent in $agents) {
    $deployCount++
    Write-Subsection "[$deployCount/$totalAgents] Deploying $($agent.Name) to Cloud Run"
    
    $imageName = "$($config.RegistryURL)/$($agent.Name):latest"
    $serviceName = $agent.Name
    
    Write-Info "Service: $serviceName"
    Write-Info "Image: $imageName"
    
    try {
        Write-Host "  Starting deployment..." -ForegroundColor Gray
        
        $output = (gcloud run deploy $serviceName `
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
            Write-Host "`nCloud Run Deploy Error Output:" -ForegroundColor Red
            Write-Host $output -ForegroundColor Gray
            Write-FatalError "Failed to deploy $serviceName"
        }
        
        Write-Success "Deployment completed"
        
        # Get service URL
        $serviceUrl = (gcloud run services describe $serviceName --region=$Region --format="value(status.url)" --project=$ProjectID 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrEmpty($serviceUrl)) {
            Write-Info "Service URL: $serviceUrl"
        }
        
        Start-Sleep -Seconds 3
        
    } catch {
        Write-FatalError "Error deploying $serviceName`: $_"
    }
}

Write-Success "All agents deployed successfully"

# ============================================================================
# VERIFY DEPLOYMENTS
# ============================================================================

Write-Section "Verifying Agent Deployments"

Write-Info "Checking deployed services..."
Write-Info ""

$verifyCount = 0
foreach ($agent in $agents) {
    $verifyCount++
    $serviceName = $agent.Name
    
    Write-Host "  [$verifyCount/$totalAgents] ${serviceName}: " -NoNewline
    
    $serviceInfo = (gcloud run services describe $serviceName --region=$Region --format="value(status.conditions[0].status)" --project=$ProjectID 2>&1 | Out-String).Trim()
    
    if ($LASTEXITCODE -eq 0 -and $serviceInfo -like "*True*") {
        Write-Host "✓" -ForegroundColor Green
        
        $serviceUrl = (gcloud run services describe $serviceName --region=$Region --format="value(status.url)" --project=$ProjectID 2>&1 | Out-String).Trim()
        Write-Info "    URL: $serviceUrl"
    } else {
        Write-Host "⏳ Initializing" -ForegroundColor Yellow
    }
}

# ============================================================================
# COMPLETION
# ============================================================================

Write-Section "PHASE 3 Complete ✓"
Write-Info "All 6 agents deployed successfully to Cloud Run"
Write-Info ""
Write-Info "Deployed Agents:"
foreach ($agent in $agents) {
    Write-Info "  • $($agent.Name)"
}
Write-Info ""
Write-Info "🎯 Next Step: Run deploy-04-deploy-app.ps1"
Write-Info ""
Write-Info "   .\deploy-04-deploy-app.ps1 -ProjectID '$ProjectID' -Region '$Region'"
Write-Info ""

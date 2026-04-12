# Justice AI Workflow - Complete Deployment Automation Script
# This script automates the entire deployment process to Google Cloud
# Prerequisites: Google Cloud SDK, PowerShell 7+, Docker Desktop

param(
    [Parameter(Mandatory=$true, HelpMessage="Google Cloud Project ID")]
    [string]$ProjectID,
    
    [Parameter(Mandatory=$false, HelpMessage="Google Cloud Region")]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false, HelpMessage="Service Account Name")]
    [string]$ServiceAccountName = "justice-ai-sa",
    
    [Parameter(Mandatory=$false, HelpMessage="Skip Docker build (use pre-built images)")]
    [switch]$SkipDockerBuild,
    
    [Parameter(Mandatory=$false, HelpMessage="Only deploy specific service")]
    [string]$DeployService = "all",
    
    [Parameter(Mandatory=$false, HelpMessage="Enable verbose logging")]
    [switch]$Verbose
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$ErrorActionPreference = "Stop"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

$config = @{
    ProjectID = $ProjectID
    Region = $Region
    ServiceAccountName = $ServiceAccountName
    ServiceAccountEmail = "$ServiceAccountName@$ProjectID.iam.gserviceaccount.com"
    RegistryRepo = "justice-ai-repository"
    RegistryURL = "$Region-docker.pkg.dev/$ProjectID/justice-ai-repository"
    
    # Services to deploy
    Services = @(
        @{ Name = "chief-justice"; Port = 8000; Authenticate = $true }
        @{ Name = "quantitative-auditor"; Port = 8001; Authenticate = $true }
        @{ Name = "legal-researcher"; Port = 8002; Authenticate = $true }
        @{ Name = "mitigator-juror"; Port = 8003; Authenticate = $true }
        @{ Name = "strict-auditor-juror"; Port = 8004; Authenticate = $true }
        @{ Name = "ethicist-juror"; Port = 8005; Authenticate = $true }
        @{ Name = "justice-ai-app"; Port = 8000; Authenticate = $false }
    )
    
    # Cloud Run configuration
    CloudRun = @{
        Memory = "2Gi"
        CPU = "2"
        Timeout = "3600"
        Concurrency = "80"
    }
    
    # IAM roles
    IAMRoles = @(
        "roles/aiplatform.admin"
        "roles/run.admin"
        "roles/storage.admin"
        "roles/firestore.admin"
        "roles/logging.logWriter"
        "roles/monitoring.metricWriter"
        "roles/secretmanager.secretAccessor"
        "roles/container.admin"
        "roles/servicenetworking.admin"
    )
    
    # GCP APIs to enable
    APIs = @(
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
    
    # Storage buckets
    Buckets = @(
        @{ Name = "justice-ai-cases"; Location = $Region }
        @{ Name = "justice-ai-reports"; Location = $Region }
        @{ Name = "justice-ai-legal-docs"; Location = $Region }
    )
}

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host "`n$('='*80)" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "$('='*80)" -ForegroundColor Cyan
}

function Write-Section {
    param([string]$Message)
    Write-Host "`n>>> $Message" -ForegroundColor Green
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
    Write-Host "✗ $Message" -ForegroundColor Red
    throw $Message
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Gray
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

function Test-Prerequisites {
    Write-Header "Validating Prerequisites"
    
    # Check gcloud CLI
    Write-Section "Checking Google Cloud SDK..."
    if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
        Write-FatalError "Google Cloud SDK (gcloud) not found. Please install it from https://cloud.google.com/sdk/docs/install"
    }
    Write-Success "Google Cloud SDK installed"
    
    # Check Docker (optional for deployment, required for building)
    if (-not $SkipDockerBuild) {
        Write-Section "Checking Docker..."
        if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
            Write-FatalError "Docker not found. Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
        }
        Write-Success "Docker installed"
    }
    
    # Check gcloud configuration
    Write-Section "Checking gcloud configuration..."
    $currentProject = (gcloud config get-value project 2>$null | Out-String).Trim()
    if ($currentProject -ne $ProjectID) {
        Write-Info "Setting gcloud project to $ProjectID..."
        gcloud config set project $ProjectID 2>$null | Out-Null
    }
    Write-Success "gcloud configured for project $ProjectID"
    
    # Check authentication
    Write-Section "Checking Google Cloud authentication..."
    $authStatus = (gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null | Out-String).Trim()
    if (-not $authStatus) {
        Write-FatalError "No active Google Cloud authentication found. Run: gcloud auth login"
    }
    Write-Success "Authenticated as: $authStatus"
}

# ============================================================================
# GCP SETUP FUNCTIONS
# ============================================================================

function Initialize-GCPProject {
    Write-Header "Initializing GCP Project"
    
    # Enable APIs
    Write-Section "Enabling required GCP APIs..."
    foreach ($api in $config.APIs) {
        Write-Info "Enabling $api..."
        gcloud services enable $api --project=$ProjectID 2>&1 | Out-Null
        Write-Success "Enabled $api"
    }
    
    # Create service account
    Write-Section "Creating service account..."
    $serviceAccountExists = (gcloud iam service-accounts describe $config.ServiceAccountEmail --project=$ProjectID 2>$null | Out-String).Trim()
    if ([string]::IsNullOrEmpty($serviceAccountExists)) {
        Write-Info "Service account does not exist. Creating..."
        gcloud iam service-accounts create $config.ServiceAccountName `
            --display-name="Justice AI Workflow Service Account" `
            --project=$ProjectID 2>$null | Out-Null
        Write-Success "Created service account: $($config.ServiceAccountEmail)"
    } else {
        Write-Success "Service account already exists: $($config.ServiceAccountEmail)"
    }
    
    # Assign IAM roles
    Write-Section "Assigning IAM roles..."
    foreach ($role in $config.IAMRoles) {
        Write-Info "Assigning role: $role..."
        gcloud projects add-iam-policy-binding $ProjectID `
            --member="serviceAccount:$($config.ServiceAccountEmail)" `
            --role="$role" `
            --condition=None `
            --quiet 2>&1 | Out-Null
        Write-Success "Assigned role: $role"
    }
    
    # Create storage buckets
    Write-Section "Creating Cloud Storage buckets..."
    foreach ($bucket in $config.Buckets) {
        $bucketName = "$($bucket.Name)-$ProjectID"
        Write-Info "Creating bucket: $bucketName..."
        $bucketExists = (gsutil ls -b "gs://$bucketName" 2>$null | Out-String).Trim()
        if ([string]::IsNullOrEmpty($bucketExists)) {
            gsutil mb -p $ProjectID -l $Region "gs://$bucketName" 2>&1 | Out-Null
            Write-Success "Created bucket: $bucketName"
        } else {
            Write-Success "Bucket already exists: $bucketName"
        }
    }
    
    # Create Artifact Registry repository
    Write-Section "Creating Artifact Registry repository..."
    Write-Info "Creating repository: $($config.RegistryRepo)..."
    $repoExists = (gcloud artifacts repositories describe $config.RegistryRepo --location=$Region --project=$ProjectID 2>$null | Out-String).Trim()
    if ([string]::IsNullOrEmpty($repoExists)) {
        gcloud artifacts repositories create $config.RegistryRepo `
            --repository-format=docker `
            --location=$Region `
            --project=$ProjectID 2>&1 | Out-Null
        Write-Success "Created Artifact Registry repository"
    } else {
        Write-Success "Artifact Registry repository already exists"
    }
    
    # Configure Docker authentication
    Write-Section "Configuring Docker authentication..."
    gcloud auth configure-docker "$Region-docker.pkg.dev" --quiet
    Write-Success "Docker authentication configured"
}

# ============================================================================
# DOCKER BUILD FUNCTIONS
# ============================================================================

function Build-DockerImages {
    Write-Header "Building Docker Images"
    
    if ($SkipDockerBuild) {
        Write-Warning "Skipping Docker build (--SkipDockerBuild flag set)"
        return
    }
    
    # Build agent images
    $agents = @("chief_justice", "quantitative_auditor", "legal_researcher", "mitigator_juror", "strict_auditor_juror", "ethicist_juror")
    
    foreach ($agent in $agents) {
        $agentName = $agent -replace "_", "-"
        Write-Section "Building image for agent: $agentName..."
        
        $imageName = "$($config.RegistryURL)/$agentName"
        $dockerfile = "agents/$agent/Dockerfile"
        $buildContext = "agents/$agent"
        
        Write-Info "Building: $imageName..."
        docker build -t "$imageName:latest" `
            -t "$imageName:$(git rev-parse --short HEAD 2>$null || 'local')" `
            -f $dockerfile `
            $buildContext
        
        if ($LASTEXITCODE -ne 0) {
            Write-FatalError "Failed to build image for agent $agentName"
        }
        Write-Success "Built image: $imageName"
    }
    
    # Build app image
    Write-Section "Building image for main application..."
    $imageName = "$($config.RegistryURL)/justice-ai-app"
    Write-Info "Building: $imageName..."
    docker build -t "$imageName:latest" `
        -t "$imageName:$(git rev-parse --short HEAD 2>$null || 'local')" `
        -f app/Dockerfile `
        app
    
    if ($LASTEXITCODE -ne 0) {
        Write-FatalError "Failed to build image for main application"
    }
    Write-Success "Built image: $imageName"
}

# ============================================================================
# DOCKER PUSH FUNCTIONS
# ============================================================================

function Push-DockerImages {
    Write-Header "Pushing Docker Images to Artifact Registry"
    
    # Push agent images
    $agents = @("chief_justice", "quantitative_auditor", "legal_researcher", "mitigator_juror", "strict_auditor_juror", "ethicist_juror")
    
    foreach ($agent in $agents) {
        $agentName = $agent -replace "_", "-"
        Write-Section "Pushing image for agent: $agentName..."
        
        $imageName = "$($config.RegistryURL)/$agentName"
        
        Write-Info "Pushing: $imageName:latest..."
        docker push "$imageName:latest"
        
        if ($LASTEXITCODE -ne 0) {
            Write-FatalError "Failed to push image for agent $agentName"
        }
        Write-Success "Pushed image: $imageName:latest"
    }
    
    # Push app image
    Write-Section "Pushing image for main application..."
    $imageName = "$($config.RegistryURL)/justice-ai-app"
    Write-Info "Pushing: $imageName:latest..."
    docker push "$imageName:latest"
    
    if ($LASTEXITCODE -ne 0) {
        Write-FatalError "Failed to push image for main application"
    }
    Write-Success "Pushed image: $imageName:latest"
}

# ============================================================================
# CLOUD RUN DEPLOYMENT FUNCTIONS
# ============================================================================

function Deploy-CloudRunService {
    param([string]$ServiceName, [bool]$Authenticate = $true)
    
    $imageName = "$($config.RegistryURL)/$ServiceName"
    
    Write-Info "Deploying Cloud Run service: $ServiceName..."
    Write-Info "  Image: $imageName"
    Write-Info "  Memory: $($config.CloudRun.Memory)"
    Write-Info "  CPU: $($config.CloudRun.CPU)"
    
    $cloudRunArgs = @(
        "run"
        "deploy"
        $ServiceName
        "--image=$imageName`:latest"
        "--platform=managed"
        "--region=$($config.Region)"
        "--memory=$($config.CloudRun.Memory)"
        "--cpu=$($config.CloudRun.CPU)"
        "--timeout=$($config.CloudRun.Timeout)"
        "--concurrency=$($config.CloudRun.Concurrency)"
        "--set-env-vars=GOOGLE_PROJECT_ID=$ProjectID,REGION=$($config.Region)"
        "--service-account=$($config.ServiceAccountEmail)"
        "--quiet"
    )
    
    # Add authentication flag
    if ($Authenticate) {
        $cloudRunArgs += "--no-allow-unauthenticated"
    } else {
        $cloudRunArgs += "--allow-unauthenticated"
    }
    
    gcloud @cloudRunArgs 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-FatalError "Failed to deploy Cloud Run service: $ServiceName"
    }
    
    Write-Success "Deployed Cloud Run service: $ServiceName"
}

function Deploy-AllServices {
    Write-Header "Deploying Services to Cloud Run"
    
    if ($DeployService -ne "all") {
        Write-Info "Deploying only service: $DeployService"
    }
    
    foreach ($service in $config.Services) {
        if ($DeployService -eq "all" -or $DeployService -eq $service.Name) {
            Deploy-CloudRunService -ServiceName $service.Name -Authenticate $service.Authenticate
        }
    }
}

# ============================================================================
# VERTEX AI SETUP FUNCTIONS
# ============================================================================

function Initialize-VertexAI {
    Write-Header "Initializing Vertex AI Resources"
    
    # Enable Vertex AI APIs (should already be enabled, but double-check)
    Write-Section "Ensuring Vertex AI APIs are enabled..."
    Write-Info "Enabling Vertex AI Generative AI API..."
    gcloud services enable aiplatform.googleapis.com --project=$ProjectID 2>&1 | Out-Null
    Write-Success "Vertex AI APIs enabled"
    
    # Create Firestore database
    Write-Section "Initializing Firestore database..."
    Write-Info "Creating Firestore database in native mode..."
    $firestoreDb = (gcloud firestore databases list --project=$ProjectID --format="value(name)" 2>$null | Out-String).Trim()
    if ([string]::IsNullOrEmpty($firestoreDb) -or $firestoreDb -eq "(default)") {
        gcloud firestore databases create `
            --location=$Region `
            --type=firestore-native `
            --project=$ProjectID 2>&1 | Out-Null
        Write-Success "Firestore database initialized"
    } else {
        Write-Success "Firestore database already exists: $firestoreDb"
    }
    
    # Create Vector Search index (simplified - full setup requires external embeddings)
    Write-Section "Setting up Vertex AI Vector Search..."
    Write-Info "Vector Search index configuration should be set up through Cloud Console"
    Write-Info "Index name: justice-ai-legal-precedents"
    Write-Info "Dimension: 768 (Vertex AI embeddings)"
    Write-Info "Algorithm: Tree-AH"
    Write-Success "Vector Search configuration noted"
    
    # Create Secret Manager secrets
    Write-Section "Setting up Secret Manager..."
    Write-Info "Creating secret for service account key..."
    
    # Get or create service account key
    $keyFile = "$ProjectID-key.json"
    if (-not (Test-Path $keyFile)) {
        Write-Info "Creating service account key..."
        gcloud iam service-accounts keys create $keyFile `
            --iam-account=$($config.ServiceAccountEmail) `
            --project=$ProjectID
        Write-Success "Created service account key: $keyFile"
    }
    
    # Store in Secret Manager
    Write-Info "Storing key in Secret Manager..."
    $secretExists = (gcloud secrets describe justice-ai-service-account-key --project=$ProjectID 2>$null | Out-String).Trim()
    if ([string]::IsNullOrEmpty($secretExists)) {
        gcloud secrets create justice-ai-service-account-key `
            --data-file=$keyFile `
            --project=$ProjectID 2>&1 | Out-Null
        Write-Success "Stored key in Secret Manager"
    } else {
        Write-Success "Secret key already exists in Secret Manager"
    }
}

# ============================================================================
# MONITORING SETUP FUNCTIONS
# ============================================================================

function Setup-Monitoring {
    Write-Header "Setting Up Monitoring and Logging"
    
    Write-Section "Enabling Cloud Logging for all services..."
    foreach ($service in $config.Services) {
        Write-Info "Service: $($service.Name)"
    }
    Write-Success "Cloud Logging enabled (automatic with Cloud Run)"
    
    Write-Section "Creating alert policies (manual setup required)..."
    Write-Info "Log in to Cloud Console to create custom alert policies for:"
    Write-Info "  - High error rates in Cloud Run services"
    Write-Info "  - Vertex AI API quota alerts"
    Write-Info "  - Storage bucket size alerts"
    Write-Info "  - Firestore quota alerts"
    Write-Success "Monitoring setup guidance provided"
}

# ============================================================================
# VERIFICATION FUNCTIONS
# ============================================================================

function Verify-Deployment {
    Write-Header "Verifying Deployment"
    
    Write-Section "Checking Cloud Run services..."
    foreach ($service in $config.Services) {
        Write-Info "Checking service: $($service.Name)..."
        $serviceUrl = (gcloud run services describe $service.Name `
            --region=$Region `
            --format="value(status.url)" `
            --project=$ProjectID 2>$null | Out-String).Trim()
        
        if (-not [string]::IsNullOrEmpty($serviceUrl)) {
            Write-Success "Service deployed: $($service.Name)"
            Write-Info "  URL: $serviceUrl"
        } else {
            Write-Warning "Service not found: $($service.Name)"
        }
    }
    
    Write-Section "Checking Artifact Registry images..."
    $images = (gcloud artifacts docker images list "$($config.RegistryURL)" `
        --project=$ProjectID `
        --format="value(name)" 2>$null | Out-String).Trim().Split("`n")
    
    if ($images -and $images[0] -ne "") {
        foreach ($image in $images) {
            if (-not [string]::IsNullOrEmpty($image)) {
                Write-Success "Image available: $(Split-Path -Leaf $image)"
            }
        }
    }
    
    Write-Section "Checking GCP resources..."
    Write-Info "Checking storage buckets..."
    foreach ($bucket in $config.Buckets) {
        $bucketName = "$($bucket.Name)-$ProjectID"
        $exists = (gsutil ls -b "gs://$bucketName" 2>$null | Out-String).Trim()
        if (-not [string]::IsNullOrEmpty($exists)) {
            Write-Success "Bucket exists: $bucketName"
        }
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    Write-Host "`n╔══════════════════════════════════════════════════════════════════════════════╗`n║             Justice AI Workflow - Automated Cloud Deployment                   ║`n╚══════════════════════════════════════════════════════════════════════════════╝`n"
    
    # Phase 1: Validation
    Test-Prerequisites
    
    # Phase 2: GCP Project Initialization
    Initialize-GCPProject
    
    # Phase 3: Docker Build & Push
    if (-not $SkipDockerBuild) {
        Build-DockerImages
        Push-DockerImages
    }
    
    # Phase 4: Deploy to Cloud Run
    Deploy-AllServices
    
    # Phase 5: Vertex AI Setup
    Initialize-VertexAI
    
    # Phase 6: Monitoring Setup
    Setup-Monitoring
    
    # Phase 7: Verification
    Verify-Deployment
    
    Write-Header "Deployment Complete!"
    Write-Host "`nNext Steps:`n" -ForegroundColor Cyan
    Write-Host "1. Access the Justice AI application at:" -ForegroundColor White
    Write-Host "   https://justice-ai-app-<autoassigned>.run.app`n" -ForegroundColor Green
    Write-Host "2. Monitor services in Cloud Console:" -ForegroundColor White
    Write-Host "   https://console.cloud.google.com/run?project=$ProjectID`n" -ForegroundColor Green
    Write-Host "3. View logs:" -ForegroundColor White
    Write-Host "   gcloud logging read 'resource.type=cloud_run_revision' --project=$ProjectID`n" -ForegroundColor Green
    Write-Host "4. Set up Vector Search index through Cloud Console for legal precedent RAG`n" -ForegroundColor Yellow
    Write-Host "5. Configure alert policies in Cloud Console for production monitoring`n" -ForegroundColor Yellow
}

# Run main execution
Main

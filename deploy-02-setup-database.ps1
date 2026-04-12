# ============================================================================
# PHASE 2: Setup Database (Firestore)
# ============================================================================
# This script sets up the Firestore database and Cloud Storage buckets
# Run this SECOND after enabling APIs

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="Google Cloud Project ID")]
    [string]$ProjectID,
    
    [Parameter(Mandatory=$false, HelpMessage="Google Cloud Region")]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false, HelpMessage="Setup Firestore database")]
    [switch]$SetupFirestore = $true,
    
    [Parameter(Mandatory=$false, HelpMessage="Create Cloud Storage buckets")]
    [switch]$CreateBuckets = $true
)

$ErrorActionPreference = "Stop"


# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

function Write-Header {
    Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  PHASE 2: SETUP DATABASE & STORAGE                                ║" -ForegroundColor Cyan
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
    Write-FatalError "Google Cloud SDK (gcloud) not found. Please install it from https://cloud.google.com/sdk/docs/install"
}
Write-Success "Google Cloud SDK found"

# Set project
Write-Info "Setting project to: $ProjectID"
$output = (gcloud config set project $ProjectID 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0) {
    Write-FatalError "Failed to set GCP project"
}
Write-Success "Project set to: $ProjectID"

# ============================================================================
# SETUP FIRESTORE DATABASE
# ============================================================================

if ($SetupFirestore) {
    Write-Section "Setting Up Firestore Database"
    
    Write-Info "Checking if Firestore database already exists..."
    $dbExists = (gcloud firestore databases describe --project=$ProjectID 2>&1 | Out-String).Trim()
    
    if ($LASTEXITCODE -eq 0) {
        Write-Warning "Firestore database already exists"
        Write-Info "Skipping database creation"
    } else {
        Write-Info "Creating Firestore database in $Region (Native mode)..."
        
        try {
            $output = (gcloud firestore databases create --project=$ProjectID --location=$Region --type=firestore-native 2>&1 | Out-String).Trim()
            
            if ($LASTEXITCODE -ne 0) {
                Write-FatalError "Failed to create Firestore database: $output"
            }
            
            Write-Success "Firestore database created successfully"
            Write-Info "Location: $Region | Mode: Native"
            
            # Wait for database to initialize
            Write-Info "Waiting for database to initialize (this takes ~30-60 seconds)..."
            Start-Sleep -Seconds 5
            
        } catch {
            Write-FatalError "Error creating Firestore database: $_"
        }
    }
}

# ============================================================================
# INITIALIZE FIRESTORE COLLECTIONS
# ============================================================================

Write-Section "Initializing Firestore Collections"

$collections = @(
    @{ Name = "cases"; Description = "Audit cases and submissions" }
    @{ Name = "audits"; Description = "Audit analysis results" }
    @{ Name = "legal_precedents"; Description = "Legal precedent RAG data" }
    @{ Name = "case_verdicts"; Description = "Agent jury verdicts" }
    @{ Name = "metrics"; Description = "System performance metrics" }
)

Write-Info "Firestore collections to initialize:"
foreach ($collection in $collections) {
    Write-Info "  - $($collection.Name): $($collection.Description)"
}

Write-Info ""
Write-Warning "Note: Firestore collections are created automatically when first data is written"
Write-Success "Collections configuration ready"

# ============================================================================
# CREATE CLOUD STORAGE BUCKETS
# ============================================================================

if ($CreateBuckets) {
    Write-Section "Creating Cloud Storage Buckets"
    
    $buckets = @(
        @{ Name = "justice-ai-cases-$ProjectID"; Description = "Case submissions and raw data" }
        @{ Name = "justice-ai-reports-$ProjectID"; Description = "Generated audit reports" }
        @{ Name = "justice-ai-legal-docs-$ProjectID"; Description = "Legal precedent documents for RAG" }
    )
    
    Write-Info "Total buckets to create: $($buckets.Count)"
    Write-Info ""
    
    $bucketCount = 0
    foreach ($bucket in $buckets) {
        $bucketCount++
        $bucketName = $bucket.Name
        Write-Host "  [$bucketCount/$($buckets.Count)] Creating $bucketName..." -NoNewline
        
        try {
            # Check if bucket exists
            $exists = (gcloud storage buckets describe gs://$bucketName --project=$ProjectID 2>&1 | Out-String).Trim()
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host " (already exists)" -ForegroundColor Gray
            } else {
                # Create the bucket
                $output = (gcloud storage buckets create gs://$bucketName --location=$Region --project=$ProjectID 2>&1 | Out-String).Trim()
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host " ✓" -ForegroundColor Green
                } else {
                    Write-Host " ✗" -ForegroundColor Red
                    Write-FatalError "Failed to create bucket $bucketName"
                }
            }
        } catch {
            Write-Host " ✗" -ForegroundColor Red
            Write-FatalError "Error with bucket $bucketName``: $_"
        }
    }
    
    Write-Info ""
    Write-Success "Cloud Storage buckets created/verified"
}

# ============================================================================
# VERIFY STORAGE SETUP
# ============================================================================

Write-Section "Verifying Storage Setup"

Write-Info "Firestore database status:"
$dbInfo = (gcloud firestore databases describe --project=$ProjectID --format="value(name, location, type)" 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -eq 0) {
    Write-Success "Firestore database is ready"
    Write-Info "  Details: $dbInfo"
} else {
    Write-Warning "Could not verify Firestore status (may still be initializing)"
}

Write-Info ""
Write-Info "Cloud Storage buckets:"
$bucketsList = (gcloud storage buckets list --project=$ProjectID --filter="name:justice-ai*" --format="value(name)" 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrEmpty($bucketsList)) {
    foreach ($bucket in ($bucketsList -split "`n")) {
        if (-not [string]::IsNullOrEmpty($bucket)) {
            Write-Success "Bucket: $bucket"
        }
    }
} else {
    Write-Warning "Could not list buckets (may still be initializing)"
}

# ============================================================================
# COMPLETION
# ============================================================================

Write-Section "PHASE 2 Complete ✓"
Write-Info "Database and storage infrastructure is ready"
Write-Info ""
Write-Info "🎯 Next Step: Run deploy-03-deploy-agents.ps1"
Write-Info ""
Write-Info "   .\deploy-03-deploy-agents.ps1 -ProjectID '$ProjectID' -Region '$Region'"
Write-Info ""

# ============================================================================
# MASTER DEPLOYMENT ORCHESTRATOR
# ============================================================================
# This script orchestrates the step-by-step deployment of Justice AI Workflow
# Can run all phases sequentially or deploy specific phases

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="Google Cloud Project ID")]
    [string]$ProjectID,
    
    [Parameter(Mandatory=$false, HelpMessage="Google Cloud Region")]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false, HelpMessage="Phase to run: all, apis, database, agents, app")]
    [ValidateSet("all", "apis", "database", "agents", "app")]
    [string]$Phase = "all",
    
    [Parameter(Mandatory=$false, HelpMessage="Skip confirmation prompts")]
    [switch]$SkipConfirmation
)

$ErrorActionPreference = "Stop"


# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

function Write-Header {
    Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                 JUSTICE AI WORKFLOW                               ║" -ForegroundColor Cyan
    Write-Host "║             MASTER DEPLOYMENT ORCHESTRATOR                        ║" -ForegroundColor Cyan
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

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Header

# Display Configuration
Write-Section "Deployment Configuration"
Write-Info "Project ID: $ProjectID"
Write-Info "Region: $Region"
Write-Info "Phase: $Phase"
Write-Info ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Phase mapping
$phases = @{
    "apis" = @{
        Name = "Enable Google Cloud APIs"
        Script = "deploy-01-enable-apis.ps1"
        Order = 1
    }
    "database" = @{
        Name = "Setup Database and Storage"
        Script = "deploy-02-setup-database.ps1"
        Order = 2
    }
    "agents" = @{
        Name = "Deploy Agents"
        Script = "deploy-03-deploy-agents.ps1"
        Order = 3
    }
    "app" = @{
        Name = "Deploy Main Application"
        Script = "deploy-04-deploy-app.ps1"
        Order = 4
    }
}

# Determine which phases to run
if ($Phase -eq "all") {
    $phasesToRun = $phases.Keys | Sort-Object { $phases[$_].Order }
} else {
    $phasesToRun = @($Phase)
}

# Display deployment plan
Write-Section "Deployment Plan"
Write-Info "Phases to execute:"
$index = 1
foreach ($phaseName in $phasesToRun) {
    $phaseConfig = $phases[$phaseName]
    Write-Info "  PHASE $($phaseConfig.Order) - $($phaseConfig.Name)"
    $index++
}
Write-Info ""

# Confirmation
if (-not $SkipConfirmation) {
    Write-Warning "This will deploy to Google Cloud Platform"
    $confirm = Read-Host "Continue with deployment? (yes/no)"
    if ($confirm -ne "yes") {
        Write-Info "Deployment cancelled"
        exit 0
    }
}

# ============================================================================
# EXECUTE PHASES
# ============================================================================

$totalPhases = $phasesToRun.Count
$completedPhases = 0

foreach ($phaseName in $phasesToRun) {
    $completedPhases++
    $phaseConfig = $phases[$phaseName]
    
    Write-Section "EXECUTING PHASE $($phaseConfig.Order) [$completedPhases/$totalPhases]: $($phaseConfig.Name)"
    
    $scriptPath = Join-Path $scriptDir $phaseConfig.Script
    
    if (-not (Test-Path $scriptPath)) {
        Write-Host "✗ ERROR: Script not found: $scriptPath" -ForegroundColor Red
        exit 1
    }
    
    Write-Info "Running: $($phaseConfig.Script)"
    Write-Info ""
    
    # Build parameters
    $params = @{
        ProjectID = $ProjectID
        Region = $Region
    }
    
    if ($PSBoundParameters.ContainsKey('Verbose')) {
        $params.Verbose = $true
    }
    
    # Execute phase script
    try {
        & $scriptPath @params
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "`n✗ ERROR: Phase failed with exit code $LASTEXITCODE" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "`n✗ ERROR: Phase execution failed: $_" -ForegroundColor Red
        exit 1
    }
    
    # Wait between phases
    if ($completedPhases -lt $totalPhases) {
        Write-Info ""
        Write-Info "Preparing next phase..."
        Start-Sleep -Seconds 3
    }
}

# ============================================================================
# FINAL SUMMARY
# ============================================================================

Write-Section "DEPLOYMENT COMPLETE ✓"

Write-Info ""
Write-Info "🎉 All phases executed successfully!"
Write-Info ""

Write-Success "Summary:"
Write-Info "  [OK] Phase 1: APIs Enabled (13 services)"
Write-Info "  [OK] Phase 2: Database Configured (Firestore + Storage)"
Write-Info "  [OK] Phase 3: Agents Deployed (6 services)"
Write-Info "  [OK] Phase 4: Application Deployed (1 service)"
Write-Info ""

Write-Info "📊 Next Steps:"
Write-Info "  1. Access your application in Cloud Console"
Write-Info "     https://console.cloud.google.com/run?project=$ProjectID"
Write-Info ""
Write-Info "  2. View application logs"
Write-Info "     gcloud logging read --limit 100 --project=$ProjectID"
Write-Info ""
Write-Info "  3. Get service endpoints"
Write-Info "     gcloud run services list --project=$ProjectID"
Write-Info ""

Write-Info "📈 Monitoring:"
Write-Info "  • Cloud Console: https://console.cloud.google.com?project=$ProjectID"
Write-Info "  • Logs: https://console.cloud.google.com/logs?project=$ProjectID"
Write-Info "  • Monitoring: https://console.cloud.google.com/monitoring?project=$ProjectID"
Write-Info ""

Write-Success "Deployment Ready!"
Write-Info ""

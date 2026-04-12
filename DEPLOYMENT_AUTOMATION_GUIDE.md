# Justice AI Workflow - Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Justice AI Workflow system to Google Cloud Platform. The deployment is fully automated using provided scripts and configurations.

**Project Location**: `d:\Gen-test-02\justice-ai-workflow\`

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Deployment Steps](#detailed-deployment-steps)
4. [Verification](#verification)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Managing the Deployment](#managing-the-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Cost Management](#cost-management)

---

## Prerequisites

### Required Tools

1. **Google Cloud SDK (gcloud CLI)**
   - Download: https://cloud.google.com/sdk/docs/install
   - Test installation: `gcloud --version`

2. **Docker Desktop** (for building images)
   - Download: https://www.docker.com/products/docker-desktop
   - Test installation: `docker --version`

3. **PowerShell 7+** (for the `deploy-to-cloud.ps1` script)
   - Windows: `winget install PowerShell`
   - Or download: https://github.com/PowerShell/PowerShell

4. **Git** (optional, for version control)
   - Download: https://git-scm.com/

### Required GCP Setup

1. **Google Cloud Project**
   - Create project: https://console.cloud.google.com/projectcreate
   - Billing enabled: https://console.cloud.google.com/billing

2. **GCP Credentials**
   - Run: `gcloud auth login`
   - Sign in with an account that has Project Editor permissions

### System Requirements

- **Disk Space**: ~50 GB (for Docker build cache and images)
- **Internet Connection**: Required for GCP APIs and Docker Hub
- **RAM**: 8 GB minimum (16 GB recommended for Docker builds)

---

## Quick Start

### Option 1: Automated Deployment (Recommended)

```powershell
# 1. Open PowerShell and navigate to project directory
cd d:\Gen-test-02\justice-ai-workflow

# 2. Run the automated deployment script
.\deploy-to-cloud.ps1 -ProjectID "my-gcp-project-id"

# The script will:
# - Enable all required GCP APIs
# - Create service account and assign IAM roles
# - Create storage buckets
# - Build Docker images
# - Push images to Artifact Registry
# - Deploy all services to Cloud Run
# - Initialize Vertex AI resources
# - Verify deployment
```

### Option 2: Manual Step-by-Step

Follow the detailed steps in [Detailed Deployment Steps](#detailed-deployment-steps) section.

---

## Detailed Deployment Steps

### Step 1: Set Up GCP Project

```powershell
# Set your project ID
$PROJECT_ID = "justice-ai-workflow-prod"  # Change this!
$REGION = "us-central1"

# Create the project (if not already created)
gcloud projects create $PROJECT_ID

# Set project as default
gcloud config set project $PROJECT_ID

# Enable billing verification
gcloud beta billing projects link $PROJECT_ID --billing-account=<BILLING_ACCOUNT_ID>
```

### Step 2: Enable Required Google Cloud APIs

```powershell
# Execute the enable all script (or run manually)
$APIs = @(
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

foreach ($api in $APIs) {
    Write-Host "Enabling $api..."
    gcloud services enable $api
}
```

### Step 3: Create Service Account and IAM Roles

```powershell
$SERVICE_ACCOUNT = "justice-ai-sa"
$SERVICE_ACCOUNT_EMAIL = "$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"

# Create service account
gcloud iam service-accounts create $SERVICE_ACCOUNT `
    --display-name="Justice AI Workflow Service Account"

# Assign IAM roles
$roles = @(
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

foreach ($role in $roles) {
    Write-Host "Assigning $role..."
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
        --role="$role"
}
```

### Step 4: Create Storage Buckets

```powershell
$REGION = "us-central1"

# Create case storage bucket
gsutil mb -p $PROJECT_ID -l $REGION gs://justice-ai-cases-$PROJECT_ID

# Create reports bucket
gsutil mb -p $PROJECT_ID -l $REGION gs://justice-ai-reports-$PROJECT_ID

# Create legal documents bucket
gsutil mb -p $PROJECT_ID -l $REGION gs://justice-ai-legal-docs-$PROJECT_ID
```

### Step 5: Set Up Artifact Registry Repository

```powershell
$REGION = "us-central1"
$REGISTRY_NAME = "justice-ai-repository"

# Create Artifact Registry repository
gcloud artifacts repositories create $REGISTRY_NAME `
    --repository-format=docker `
    --location=$REGION

# Configure Docker authentication
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
```

### Step 6: Build Docker Images

```powershell
cd d:\Gen-test-02\justice-ai-workflow

$REGISTRY_URL = "$REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_NAME"

# Build Chief Justice image
docker build -t "$REGISTRY_URL/chief-justice:latest" -f agents/chief_justice/Dockerfile agents/chief_justice

# Build Quantitative Auditor image
docker build -t "$REGISTRY_URL/quantitative-auditor:latest" -f agents/quantitative_auditor/Dockerfile agents/quantitative_auditor

# Build Legal Researcher image
docker build -t "$REGISTRY_URL/legal-researcher:latest" -f agents/legal_researcher/Dockerfile agents/legal_researcher

# Build Mitigator Juror image
docker build -t "$REGISTRY_URL/mitigator-juror:latest" -f agents/mitigator_juror/Dockerfile agents/mitigator_juror

# Build Strict Auditor Juror image
docker build -t "$REGISTRY_URL/strict-auditor-juror:latest" -f agents/strict_auditor_juror/Dockerfile agents/strict_auditor_juror

# Build Ethicist Juror image
docker build -t "$REGISTRY_URL/ethicist-juror:latest" -f agents/ethicist_juror/Dockerfile agents/ethicist_juror

# Build Main Application image
docker build -t "$REGISTRY_URL/justice-ai-app:latest" -f app/Dockerfile app
```

### Step 7: Push Images to Artifact Registry

```powershell
$REGISTRY_URL = "$REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_NAME"

# Push all images
docker push "$REGISTRY_URL/chief-justice:latest"
docker push "$REGISTRY_URL/quantitative-auditor:latest"
docker push "$REGISTRY_URL/legal-researcher:latest"
docker push "$REGISTRY_URL/mitigator-juror:latest"
docker push "$REGISTRY_URL/strict-auditor-juror:latest"
docker push "$REGISTRY_URL/ethicist-juror:latest"
docker push "$REGISTRY_URL/justice-ai-app:latest"

# Verify images
gcloud artifacts docker images list "$REGISTRY_URL"
```

### Step 8: Deploy Services to Cloud Run

```powershell
$REGION = "us-central1"
$REGISTRY_URL = "$REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_NAME"
$SERVICE_ACCOUNT_EMAIL = "justice-ai-sa@$PROJECT_ID.iam.gserviceaccount.com"

# Define Cloud Run configuration
$CloudRunConfig = @{
    Memory = "2Gi"
    CPU = "2"
    Timeout = "3600"
    Concurrency = "80"
}

# Deploy Chief Justice Agent
gcloud run deploy chief-justice `
    --image="$REGISTRY_URL/chief-justice:latest" `
    --platform=managed `
    --region=$REGION `
    --memory=$CloudRunConfig.Memory `
    --cpu=$CloudRunConfig.CPU `
    --timeout=$CloudRunConfig.Timeout `
    --concurrency=$CloudRunConfig.Concurrency `
    --set-env-vars="GOOGLE_PROJECT_ID=$PROJECT_ID,REGION=$REGION" `
    --service-account=$SERVICE_ACCOUNT_EMAIL `
    --no-allow-unauthenticated

# Deploy Quantitative Auditor
gcloud run deploy quantitative-auditor `
    --image="$REGISTRY_URL/quantitative-auditor:latest" `
    --platform=managed `
    --region=$REGION `
    --memory=$CloudRunConfig.Memory `
    --cpu=$CloudRunConfig.CPU `
    --timeout=$CloudRunConfig.Timeout `
    --concurrency=$CloudRunConfig.Concurrency `
    --set-env-vars="GOOGLE_PROJECT_ID=$PROJECT_ID,REGION=$REGION" `
    --service-account=$SERVICE_ACCOUNT_EMAIL `
    --no-allow-unauthenticated

# Deploy Legal Researcher
gcloud run deploy legal-researcher `
    --image="$REGISTRY_URL/legal-researcher:latest" `
    --platform=managed `
    --region=$REGION `
    --memory=$CloudRunConfig.Memory `
    --cpu=$CloudRunConfig.CPU `
    --timeout=$CloudRunConfig.Timeout `
    --concurrency=$CloudRunConfig.Concurrency `
    --set-env-vars="GOOGLE_PROJECT_ID=$PROJECT_ID,REGION=$REGION" `
    --service-account=$SERVICE_ACCOUNT_EMAIL `
    --no-allow-unauthenticated

# Deploy Mitigator Juror
gcloud run deploy mitigator-juror `
    --image="$REGISTRY_URL/mitigator-juror:latest" `
    --platform=managed `
    --region=$REGION `
    --memory=$CloudRunConfig.Memory `
    --cpu=$CloudRunConfig.CPU `
    --timeout=$CloudRunConfig.Timeout `
    --concurrency=$CloudRunConfig.Concurrency `
    --set-env-vars="GOOGLE_PROJECT_ID=$PROJECT_ID,REGION=$REGION" `
    --service-account=$SERVICE_ACCOUNT_EMAIL `
    --no-allow-unauthenticated

# Deploy Strict Auditor Juror
gcloud run deploy strict-auditor-juror `
    --image="$REGISTRY_URL/strict-auditor-juror:latest" `
    --platform=managed `
    --region=$REGION `
    --memory=$CloudRunConfig.Memory `
    --cpu=$CloudRunConfig.CPU `
    --timeout=$CloudRunConfig.Timeout `
    --concurrency=$CloudRunConfig.Concurrency `
    --set-env-vars="GOOGLE_PROJECT_ID=$PROJECT_ID,REGION=$REGION" `
    --service-account=$SERVICE_ACCOUNT_EMAIL `
    --no-allow-unauthenticated

# Deploy Ethicist Juror
gcloud run deploy ethicist-juror `
    --image="$REGISTRY_URL/ethicist-juror:latest" `
    --platform=managed `
    --region=$REGION `
    --memory=$CloudRunConfig.Memory `
    --cpu=$CloudRunConfig.CPU `
    --timeout=$CloudRunConfig.Timeout `
    --concurrency=$CloudRunConfig.Concurrency `
    --set-env-vars="GOOGLE_PROJECT_ID=$PROJECT_ID,REGION=$REGION" `
    --service-account=$SERVICE_ACCOUNT_EMAIL `
    --no-allow-unauthenticated

# Deploy Main Application (allow unauthenticated)
gcloud run deploy justice-ai-app `
    --image="$REGISTRY_URL/justice-ai-app:latest" `
    --platform=managed `
    --region=$REGION `
    --memory=$CloudRunConfig.Memory `
    --cpu=$CloudRunConfig.CPU `
    --timeout=$CloudRunConfig.Timeout `
    --concurrency=$CloudRunConfig.Concurrency `
    --set-env-vars="GOOGLE_PROJECT_ID=$PROJECT_ID,REGION=$REGION" `
    --service-account=$SERVICE_ACCOUNT_EMAIL `
    --allow-unauthenticated
```

### Step 9: Initialize Vertex AI Resources

```powershell
# Enable Firestore database
gcloud firestore databases create `
    --location=$REGION `
    --type=firestore-native

# Create Secret Manager secrets
$keyFile = "$PROJECT_ID-key.json"

# Generate service account key
gcloud iam service-accounts keys create $keyFile `
    --iam-account=$SERVICE_ACCOUNT_EMAIL

# Store in Secret Manager
Get-Content $keyFile | gcloud secrets create justice-ai-service-account-key `
    --data-file=-

# Set up Vector Search (requires index configuration through Cloud Console)
Write-Host "Vector Search index needs to be created through Cloud Console:"
Write-Host "https://console.cloud.google.com/ai/vector-search"
```

### Step 10: Configure Environment Variables and Secrets

Create `.env.production` file:

```bash
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_REGION=us-central1
GOOGLE_SERVICE_ACCOUNT_EMAIL=justice-ai-sa@your-project-id.iam.gserviceaccount.com

# Vertex AI Models
GEMINI_MODEL=gemini-1.5-pro
GEMINI_FLASH_MODEL=gemini-1.5-flash

# Vector Search
VECTOR_SEARCH_INDEX_ID=justice-ai-legal-precedents
VECTOR_SEARCH_ENDPOINT=projects/{project-id}/locations/{region}/indexes/{index-id}
VECTOR_SEARCH_DEPLOYED_INDEX_ID=justice-ai-legal-precedents

# Cloud Storage
CASES_BUCKET=gs://justice-ai-cases-{project-id}
REPORTS_BUCKET=gs://justice-ai-reports-{project-id}
LEGAL_DOCS_BUCKET=gs://justice-ai-legal-docs-{project-id}

# Firestore
FIRESTORE_COLLECTION_CASES=audit_cases
FIRESTORE_COLLECTION_REPORTS=audit_reports

# Cloud Run Service URLs
CHIEF_JUSTICE_SERVICE_URL=https://chief-justice-{auto-assigned}.run.app
QUANTITATIVE_AUDITOR_SERVICE_URL=https://quantitative-auditor-{auto-assigned}.run.app
LEGAL_RESEARCHER_SERVICE_URL=https://legal-researcher-{auto-assigned}.run.app
MITIGATOR_JUROR_SERVICE_URL=https://mitigator-juror-{auto-assigned}.run.app
STRICT_AUDITOR_JUROR_SERVICE_URL=https://strict-auditor-juror-{auto-assigned}.run.app
ETHICIST_JUROR_SERVICE_URL=https://ethicist-juror-{auto-assigned}.run.app
```

---

## Verification

### Verify Cloud Run Services

```powershell
# List all deployed services
gcloud run services list --region=$REGION

# Get service URL for main application
gcloud run services describe justice-ai-app `
    --region=$REGION `
    --format="value(status.url)"

# Test service health endpoint
$appUrl = (gcloud run services describe justice-ai-app `
    --region=$REGION `
    --format="value(status.url)").Trim()

Invoke-WebRequest -Uri "$appUrl/health"
```

### Check Artifact Registry Images

```powershell
# List all images
gcloud artifacts docker images list "$REGISTRY_URL"

# List tags for specific image
gcloud artifacts docker images describe "$REGISTRY_URL/justice-ai-app:latest"
```

### Verify Firestore Database

```powershell
# Describe Firestore database
gcloud firestore databases describe --location=$REGION

# List collections (should be empty initially)
gcloud firestore collections list
```

### Check Service Account

```powershell
# Describe service account
gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL

# List IAM bindings
gcloud projects get-iam-policy $PROJECT_ID `
    --flatten="bindings[].members" `
    --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT_EMAIL"
```

---

## Post-Deployment Configuration

### 1. Update Cloud Run Service Environment Variables

```powershell
$REGION = "us-central1"
$PROJECT_ID = "your-project-id"

# Get the service URLs from deployed services
$chiefJusticeUrl = (gcloud run services describe chief-justice --region=$REGION --format="value(status.url)").Trim()
$quantAuditorUrl = (gcloud run services describe quantitative-auditor --region=$REGION --format="value(status.url)").Trim()
$legalResearcherUrl = (gcloud run services describe legal-researcher --region=$REGION --format="value(status.url)").Trim()
$mitigatorJurorUrl = (gcloud run services describe mitigator-juror --region=$REGION --format="value(status.url)").Trim()
$strictAuditorUrl = (gcloud run services describe strict-auditor-juror --region=$REGION --format="value(status.url)").Trim()
$ethicistJurorUrl = (gcloud run services describe ethicist-juror --region=$REGION --format="value(status.url)").Trim()

# Update Chief Justice service with other service URLs
gcloud run services update chief-justice `
    --region=$REGION `
    --update-env-vars=`
"QUANTITATIVE_AUDITOR_URL=$quantAuditorUrl,`
LEGAL_RESEARCHER_URL=$legalResearcherUrl,`
MITIGATOR_JUROR_URL=$mitigatorJurorUrl,`
STRICT_AUDITOR_JUROR_URL=$strictAuditorUrl,`
ETHICIST_JUROR_URL=$ethicistJurorUrl"
```

### 2. Set Up Vector Search Index

```powershell
# Through Cloud Console:
# 1. Go to Vertex AI > Vector Search
# 2. Create new index:
#    - Name: justice-ai-legal-precedents
#    - Index type: Tree-AH
#    - Dimension: 768
#    - Distance measure: Cosine
# 3. After creation, deploy index to endpoint

# Via gcloud (advanced):
# gcloud ai index-endpoints create justice-ai-index-endpoint --region=$REGION
```

### 3. Set Up Cloud Logging

```powershell
# View logs for specific service
gcloud logging read "'resource.type=cloud_run_revision' AND 'resource.labels.service_name=justice-ai-app'" `
    --limit=50 `
    --format=json

# Set up log sink for archival
gcloud logging sinks create justice-ai-logs-sink `
    "storage.googleapis.com/justice-ai-logs-$PROJECT_ID" `
    --log-filter='resource.type=cloud_run_revision'
```

### 4. Create Cloud Monitoring Alerts

Create alert policies through Cloud Console:

1. **Navigate**: https://console.cloud.google.com/monitoring/alerting/policies
2. **Create Policy** for each:
   - Cloud Run error rate > 5%
   - Vertex AI API quota exceeded
   - Storage bucket size > 100 GB
   - Request latency > 5 seconds

---

## Managing the Deployment

### Scaling Services

```powershell
# Update service memory and CPU
gcloud run services update justice-ai-app `
    --region=$REGION `
    --memory=4Gi `
    --cpu=4

# Update concurrent request limit
gcloud run services update justice-ai-app `
    --region=$REGION `
    --concurrency=200
```

### Deploying Updates

```powershell
# Rebuild image with new code
docker build -t "$REGISTRY_URL/justice-ai-app:v2" -f app/Dockerfile app

# Push updated image
docker push "$REGISTRY_URL/justice-ai-app:v2"

# Redeploy service
gcloud run deploy justice-ai-app `
    --image="$REGISTRY_URL/justice-ai-app:v2" `
    --region=$REGION
```

### Monitoring Service Health

```powershell
# Get service details
gcloud run services describe justice-ai-app --region=$REGION

# View recent revisions
gcloud run revisions list --service=justice-ai-app --region=$REGION

# View service metrics
gcloud run services describe justice-ai-app `
    --region=$REGION `
    --format="value(status.conditions)"
```

### Accessing Service Logs

```powershell
# Stream logs for specific service
gcloud logging read "resource.labels.service_name=justice-ai-app" `
    --region=$REGION `
    --tail

# Export logs to BigQuery for analysis
gcloud logging sinks create bigquery-export `
    "bigquery.googleapis.com/projects/$PROJECT_ID/datasets/audit_logs"
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Docker Build Failures

**Error**: `Docker: permission denied` or `docker: command not found`

**Solution**:
```powershell
# Ensure Docker Desktop is running
# Restart Docker daemon
Restart-Service docker -Confirm:$false

# Check Docker installation
docker ps
```

#### Issue 2: Artifact Registry Push Failures

**Error**: `denied: User not authorized` or `permission denied`

**Solution**:
```powershell
# Re-authenticate with gcloud
gcloud auth configure-docker $REGION-docker.pkg.dev

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID `
    --flatten="bindings[].members" `
    --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT_EMAIL"
```

#### Issue 3: Cloud Run Deployment Fails

**Error**: `Cloud Run service failed to deploy` or `Revision was not created`

**Solution**:
```powershell
# Check service account has required roles
gcloud projects get-iam-policy $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL"

# View deployment events
gcloud run services describe justice-ai-app --region=$REGION --format=json | jq '.status.conditions'

# Check API is enabled
gcloud services list --enabled | grep run.googleapis.com
```

#### Issue 4: High Latency or Timeouts

**Error**: `Request timeout` or `504 Gateway Timeout`

**Solution**:
```powershell
# Increase service timeout
gcloud run services update justice-ai-app `
    --timeout=3600 `
    --region=$REGION

# Scale up memory
gcloud run services update justice-ai-app `
    --memory=4Gi `
    --region=$REGION

# Check concurrent requests
gcloud run services describe justice-ai-app `
    --region=$REGION `
    --format="value(spec.template.spec.containerConcurrency)"
```

#### Issue 5: Vertex AI API Errors

**Error**: `Cannot connect to Vertex AI` or `Model not found`

**Solution**:
```powershell
# Verify Vertex AI API is enabled
gcloud services list --enabled | grep aiplatform

# Check service account has aiplatform.admin role
gcloud projects get-iam-policy $PROJECT_ID `
    --flatten="bindings[].members" `
    --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT_EMAIL AND bindings.role:roles/aiplatform.admin"

# Test Gemini API access
gcloud ai models describe gemini-1.5-pro --region=$REGION
```

#### Issue 6: Storage Bucket Access Denied

**Error**: `403 Forbidden` when accessing buckets

**Solution**:
```powershell
# Grant storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/storage.admin"

# Check bucket permissions
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT_EMAIL:objectAdmin gs://justice-ai-cases-$PROJECT_ID
```

### Debug Commands

```powershell
# View Cloud Run service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=justice-ai-app" `
    --limit=100 `
    --format=json

# Stream logs in real-time
gcloud logging read "resource.type=cloud_run_revision" --follow

# Check service health endpoint
$appUrl = (gcloud run services describe justice-ai-app --region=$REGION --format="value(status.url)").Trim()
Invoke-WebRequest -Uri "$appUrl/health" -Verbose

# Test inter-service communication
$chiefUrl = (gcloud run services describe chief-justice --region=$REGION --format="value(status.url)").Trim()
Invoke-WebRequest -Uri "$chiefUrl/health" -Headers @{"Authorization"="Bearer $(gcloud auth print-access-token)"}
```

---

## Cost Management

### Estimated Monthly Costs (Production)

| Service | Estimated Cost |
|---------|-----------------|
| Cloud Run (7 services @ 100 invocations/day) | $35-50 |
| Vertex AI Gemini API (50k monthly tokens) | $25-40 |
| Vertex AI Vector Search (1GB index) | $15-25 |
| Firestore (10GB storage, 1M reads/month) | $20-30 |
| Cloud Storage (100GB) | $10-15 |
| Cloud Logging (50GB logs/month) | $15-25 |
| **Total Estimated** | **$120-185/month** |

### Cost Optimization Tips

```powershell
# 1. Set up budget alerts
gcloud billing budgets create `
    --billing-account=$BILLING_ACCOUNT `
    --display-name="Justice AI Budget" `
    --budget-amount=200 `
    --threshold-rule=percent=50 `
    --threshold-rule=percent=90 `
    --threshold-rule=percent=100

# 2. Reduce Cloud Run concurrency during off-hours
# Schedule via Cloud Scheduler

# 3. archive old logs to Cloud Storage
gcloud logging sinks create archive-logs `
    "storage.googleapis.com/justice-ai-archive-logs" `
    --log-filter='timestamp<"2024-01-01T00:00:00Z"'

# 4. Use committed use discounts
# Configure through: https://console.cloud.google.com/billing/commitments
```

### Monitor Spending

```powershell
# View billing data
gcloud billing accounts list

# Set up cost anomaly detection
# Via Cloud Console: Billing > Budgets & alerts > Create anomaly alert

# Export billing data to BigQuery
gcloud billing exports create bigquery-export `
    --dataset-id=billing_data `
    --billing-account=$BILLING_ACCOUNT
```

---

## Database Schema (Firestore)

### Case Collection

```json
{
  "caseId": "string",
  "createdAt": "timestamp",
  "status": "string",
  "algorithm": "string",
  "dataset": "string",
  "features": ["string"],
  "outcomeVariable": "string",
  "protectedCharacteristics": ["string"]
}
```

### Reports Collection

```json
{
  "reportId": "string",
  "caseId": "string",
  "verdict": "string",
  "biasScore": "number",
  "correctedScore": "number",
  "riskLevel": "string",
  "generatedAt": "timestamp",
  "metrics": {
    "disparateImpactRatio": "number",
    "statisticalParity": "number",
    "fairnessScore": "number"
  }
}
```

---

## Support and Resources

- **GCP Documentation**: https://cloud.google.com/docs
- **Vertex AI Docs**: https://cloud.google.com/vertex-ai/docs
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Troubleshooting**: Run `gcloud help` for individual command help

---

## Security Best Practices

1. **Service Account Keys**: Delete old keys periodically
2. **Secret Manager**: Store all sensitive credentials
3. **IAM Roles**: Use principle of least privilege
4. **VPC Service Control**: Implement in production
5. **Cloud Audit Logs**: Enable for compliance tracking
6. **API Rate Limiting**: Implement in client code

---

## Summary

After successful deployment, your Justice AI Workflow system will:

✅ Run 7 Cloud Run services (chief justice + 6 agents + app)
✅ Use Vertex AI for all AI/ML operations
✅ Store cases and reports in Firestore
✅ Perform legal precedent searches via Vector Search
✅ Generate audit reports and verdicts
✅ Log all activities for compliance

**Access your deployment**:
```
https://justice-ai-app-{random-string}.run.app
```

**Monitor costs and performance**:
```
https://console.cloud.google.com/run?project={PROJECT_ID}
https://console.cloud.google.com/billing?project={PROJECT_ID}
```

---

*Last Updated: 2024*
*Project: Justice AI Workflow on Google Cloud Platform*

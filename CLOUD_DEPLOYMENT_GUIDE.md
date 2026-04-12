# 🚀 Justice AI Workflow - Google Cloud Deployment Guide

## Complete Production Deployment on Google Cloud Platform

This guide covers everything needed to deploy **Justice AI Workflow** to Google Cloud using **Vertex AI** exclusively.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Required GCP Services & APIs](#required-gcp-services--apis)
3. [Pre-Deployment Setup](#pre-deployment-setup)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Configuration & Secrets Management](#configuration--secrets-management)
6. [Monitoring & Logging](#monitoring--logging)
7. [Cost Estimation](#cost-estimation)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Local Requirements
- Google Cloud SDK (gcloud CLI)
- Docker & Docker Desktop
- Python 3.10+
- Git

### GCP Requirements
- **Active Google Cloud Project**
- **Billing Account enabled**
- **Appropriate IAM permissions** (Project Owner or custom role)

### Installation

#### 1. Install Google Cloud SDK
```bash
# Windows (PowerShell)
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:TEMP\GoogleCloudSDKInstaller.exe")
& "$env:TEMP\GoogleCloudSDKInstaller.exe"

# Or use Chocolatey
choco install google-cloud-sdk

# Verify installation
gcloud --version
```

#### 2. Authenticate with Google Cloud
```bash
gcloud auth login
gcloud auth application-default login
```

#### 3. Set Default Project
```bash
$PROJECT_ID = "your-project-id"

gcloud config set project $PROJECT_ID
gcloud config list
```

---

## ✅ Required GCP Services & APIs

### **1. Core AI Services**
- ✅ **Vertex AI** (AI Platform) - Main orchestration
- ✅ **Vertex AI Generative AI (Gemini)** - LLM for agents
- ✅ **Vertex AI Vector Search** - Vector database for legal precedents (State 3 RAG)

### **2. Compute Services**
- ✅ **Cloud Run** - Container orchestration for agents
- ✅ **Artifact Registry** - Container image storage
- ✅ **Cloud Build** - CI/CD pipeline

### **3. Storage & Data**
- ✅ **Cloud Storage** - Store case files, legal documents, reports
- ✅ **Cloud Firestore** - NoSQL database for case metadata
- ✅ **Vertex AI Feature Store** - Feature management (optional)

### **4. Networking & Security**
- ✅ **Cloud IAM** - Identity & access management
- ✅ **Secret Manager** - Store API keys & credentials
- ✅ **VPC (Virtual Private Cloud)** - Network isolation

### **5. Logging & Monitoring**
- ✅ **Cloud Logging** - Centralized logging
- ✅ **Cloud Monitoring** - Metrics & alerting
- ✅ **Cloud Trace** - Distributed tracing

### **6. Optional Services**
- 📊 **BigQuery** - Data warehouse for audit analytics
- 📈 **Cloud Tasks** - Background job queues
- 🔐 **Cloud KMS** - Key management for encryption

---

## Pre-Deployment Setup

### Step 1: Create GCP Project
```bash
# Set variables
$PROJECT_ID = "justice-ai-workflow-prod"
$PROJECT_NAME = "Justice AI Workflow"
$REGION = "us-central1"

# Create new project
gcloud projects create $PROJECT_ID `
    --name=$PROJECT_NAME `
    --set-as-default

# Wait for project creation
Start-Sleep -Seconds 10

# Verify project
gcloud projects describe $PROJECT_ID
```

### Step 2: Enable Required APIs
```bash
# Enable all required APIs
gcloud services enable \
    aiplatform.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    storage-api.googleapis.com \
    firestore.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    cloudtrace.googleapis.com \
    secretmanager.googleapis.com \
    iam.googleapis.com \
    container.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled | Select-String "aiplatform\|run\|artifactregistry"
```

### Step 3: Create Service Account
```bash
# Variables
$SERVICE_ACCOUNT_NAME = "justice-ai-sa"
$SERVICE_ACCOUNT_EMAIL = "$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Create service account
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME `
    --display-name="Justice AI Workflow Service Account" `
    --description="Service account for Justice AI Agents"

# Assign roles
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/firestore.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/secretmanager.secretAccessor"
```

### Step 4: Create Service Account Key
```bash
# Create and download key
gcloud iam service-accounts keys create ./service-account-key.json `
    --iam-account=$SERVICE_ACCOUNT_EMAIL

# Verify key created
Write-Host "Service account key created at: ./service-account-key.json"
```

### Step 5: Create Cloud Storage Buckets
```bash
# Variables
$BUCKET_CASES = "justice-ai-case-files-$PROJECT_ID"
$BUCKET_REPORTS = "justice-ai-reports-$PROJECT_ID"
$BUCKET_LEGAL = "justice-ai-legal-docs-$PROJECT_ID"

# Create buckets
gsutil mb -p $PROJECT_ID gs://$BUCKET_CASES
gsutil mb -p $PROJECT_ID gs://$BUCKET_REPORTS
gsutil mb -p $PROJECT_ID gs://$BUCKET_LEGAL

# Set permissions
gsutil iam ch "serviceAccount:$SERVICE_ACCOUNT_EMAIL:objectAdmin" gs://$BUCKET_CASES
gsutil iam ch "serviceAccount:$SERVICE_ACCOUNT_EMAIL:objectAdmin" gs://$BUCKET_REPORTS
gsutil iam ch "serviceAccount:$SERVICE_ACCOUNT_EMAIL:objectAdmin" gs://$BUCKET_LEGAL

Write-Host "Buckets created successfully!"
```

### Step 6: Create Artifact Registry Repository
```bash
# Create container repository
gcloud artifacts repositories create justice-ai-repository `
    --repository-format=docker `
    --location=$REGION `
    --description="Container images for Justice AI agents"

# Verify creation
gcloud artifacts repositories list

Write-Host "Artifact Registry repository created!"
```

---

## Step-by-Step Deployment

### Phase 1: Prepare Docker Images

#### 1.1 Configure Docker Authentication
```bash
# Configure gcloud as Docker credential helper
gcloud auth configure-docker $REGION-docker.pkg.dev

# Verify authentication
Write-Host "Docker authentication configured for $REGION"
```

#### 1.2 Build & Push Images
```bash
# Variables
$REGISTRY = "$REGION-docker.pkg.dev/$PROJECT_ID/justice-ai-repository"

# Array of agents
$AGENTS = @(
    "chief_justice",
    "quantitative_auditor",
    "legal_researcher",
    "mitigator_juror",
    "strict_auditor_juror",
    "ethicist_juror"
)

# Build and push each agent
foreach ($agent in $AGENTS) {
    Write-Host "Building and pushing $agent..."
    
    docker build -t "$REGISTRY/$agent`:latest" "./agents/$agent"
    docker push "$REGISTRY/$agent`:latest"
    
    Write-Host "$agent pushed successfully!"
}

# Build and push main app
Write-Host "Building and pushing main app..."
docker build -t "$REGISTRY/justice-ai-app`:latest" "./app"
docker push "$REGISTRY/justice-ai-app`:latest"

Write-Host "All images pushed to Artifact Registry!"
```

---

### Phase 2: Deploy Agents to Cloud Run

#### 2.1 Deploy Each Agent Service
```bash
# Variables
$REGION = "us-central1"
$SERVICE_ACCOUNT_EMAIL = "justice-ai-sa@$PROJECT_ID.iam.gserviceaccount.com"
$REGISTRY = "$REGION-docker.pkg.dev/$PROJECT_ID/justice-ai-repository"

# Function to deploy agent
function Deploy-Agent {
    param($AGENT_NAME, $PORT = 8000)
    
    Write-Host "Deploying $AGENT_NAME to Cloud Run..."
    
    gcloud run deploy "$AGENT_NAME" `
        --image "$REGISTRY/$AGENT_NAME`:latest" `
        --platform managed `
        --region $REGION `
        --memory 2Gi `
        --cpu 2 `
        --timeout 3600 `
        --set-env-vars "GOOGLE_PROJECT_ID=$PROJECT_ID,REGION=$REGION,AGENT_NAME=$AGENT_NAME,AGENT_PORT=$PORT" `
        --service-account $SERVICE_ACCOUNT_EMAIL `
        --no-allow-unauthenticated `
        --no-traffic
    
    Write-Host "$AGENT_NAME deployed!"
}

# Deploy all agents
$AGENTS | ForEach-Object { Deploy-Agent $_ }

# Deploy main app (allow unauthenticated for UI)
Write-Host "Deploying main application..."
gcloud run deploy "justice-ai-app" `
    --image "$REGISTRY/justice-ai-app`:latest" `
    --platform managed `
    --region $REGION `
    --memory 2Gi `
    --cpu 2 `
    --timeout 3600 `
    --set-env-vars "GOOGLE_PROJECT_ID=$PROJECT_ID,REGION=$REGION" `
    --service-account $SERVICE_ACCOUNT_EMAIL `
    --allow-unauthenticated

Write-Host "All services deployed!"
```

#### 2.2 Get Service URLs
```bash
# Get URLs for all deployed services
Write-Host "Justice AI Workflow Services:"
Write-Host "=================================="`n

gcloud run services list --platform=managed --region=$REGION | Select-String "justice-ai"

# Get specific service URLs
$APP_URL = gcloud run services describe justice-ai-app --platform managed --region $REGION --format 'value(status.url)'
$CHIEF_URL = gcloud run services describe chief_justice --platform managed --region $REGION --format 'value(status.url)'

Write-Host "`nMain Application: $APP_URL"
Write-Host "Chief Justice Agent: $CHIEF_URL"
```

---

### Phase 3: Configure Vertex AI Resources

#### 3.1 Set Up Vector Database for Legal Precedents (State 3 - RAG)
```bash
# Create Vertex AI Vector Search Index
Write-Host "Creating Vertex AI Vector Search Index..."

# Create embeddings configuration
$VECTOR_CONFIG = @{
    "displayName" = "justice-ai-legal-precedents"
    "indexConfig" = @{
        "treeAhConfig" = @{
            "leafNodeEmbeddingCount" = 1000
        }
    }
    "description" = "Vector index for legal precedents and case law"
} | ConvertTo-Json

# Create index
gcloud ai indexes create `
    --display-name="justice-ai-legal-precedents" `
    --region=$REGION `
    --description="Vector search for legal precedents"

Write-Host "Vector Search Index created!"
```

#### 3.2 Configure Gemini API for Jury Agents
```bash
# Verify Gemini API is enabled
gcloud services enable generativelanguage.googleapis.com

# Create API key for Gemini (optional, for testing)
Write-Host "Gemini API is enabled and ready for use!"
```

#### 3.3 Initialize Firestore for Case Storage
```bash
# Create Firestore database
gcloud firestore databases create `
    --region=$REGION `
    --type=firestore-native

# Wait for database creation
Start-Sleep -Seconds 30

Write-Host "Firestore database created!"
```

---

### Phase 4: Set Environment Variables & Secrets

#### 4.1 Store Secrets in Secret Manager
```bash
# Create secrets
echo $PROJECT_ID | gcloud secrets create PROJECT_ID --data-file=-
echo $REGION | gcloud secrets create REGION --data-file=-
echo "us-central1-docker.pkg.dev/$PROJECT_ID/justice-ai-repository" | `
    gcloud secrets create ARTIFACT_REGISTRY_URL --data-file=-

# Grant service account access
gcloud secrets add-iam-policy-binding PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/secretmanager.secretAccessor"

Write-Host "Secrets stored in Secret Manager!"
```

#### 4.2 Create Cloud Run Configuration File
```bash
# Create env file for Cloud Run services
$ENV_CONFIG = @"
GOOGLE_PROJECT_ID=$PROJECT_ID
GOOGLE_REGION=$REGION
ARTIFACT_REGISTRY=$REGISTRY
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_MONITORING=true
ENABLE_TRACING=true
"@

$ENV_CONFIG | Set-Content ./cloud-run.env

Write-Host "Cloud Run configuration created!"
```

---

## Configuration & Secrets Management

### Create `.env.production` File
```bash
# Navigate to project
cd d:\Gen-test-02\justice-ai-workflow

# Create production environment file
$PROD_ENV = @"
# Google Cloud Configuration
GOOGLE_PROJECT_ID=$PROJECT_ID
GOOGLE_REGION=us-central1
GOOGLE_CREDENTIALS_JSON=/secrets/service-account-key.json

# API Endpoints (Cloud Run URLs)
CHIEF_JUSTICE_URL=https://chief-justice-<random>.us-central1.run.app
QUANTITATIVE_AUDITOR_URL=https://quantitative-auditor-<random>.us-central1.run.app
LEGAL_RESEARCHER_URL=https://legal-researcher-<random>.us-central1.run.app
MITIGATOR_JUROR_URL=https://mitigator-juror-<random>.us-central1.run.app
STRICT_AUDITOR_JUROR_URL=https://strict-auditor-juror-<random>.us-central1.run.app
ETHICIST_JUROR_URL=https://ethicist-juror-<random>.us-central1.run.app

# Vertex AI Configuration
VERTEX_AI_PROJECT_ID=$PROJECT_ID
VERTEX_AI_REGION=us-central1
GEMINI_MODEL=gemini-1.5-pro
GEMINI_FLASH_MODEL=gemini-1.5-flash

# Storage Configuration
CASE_BUCKET=gs://justice-ai-case-files-$PROJECT_ID
REPORTS_BUCKET=gs://justice-ai-reports-$PROJECT_ID
LEGAL_DOCS_BUCKET=gs://justice-ai-legal-docs-$PROJECT_ID

# Database Configuration
FIRESTORE_DATABASE_ID=(default)
VECTOR_INDEX_NAME=justice-ai-legal-precedents

# Application Configuration
API_PORT=8080
API_WORKERS=4
DEBUG=false
LOG_LEVEL=INFO

# Service Configuration
SERVICE_ACCOUNT_EMAIL=justice-ai-sa@$PROJECT_ID.iam.gserviceaccount.com
ARTIFACT_REGISTRY_URL=$REGISTRY
"@

$PROD_ENV | Set-Content .\.env.production

Write-Host ".env.production created!"
```

---

## Monitoring & Logging

### View Cloud Logs
```bash
# View recent logs for main app
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=justice-ai-app" `
    --limit 50 `
    --format json `
    --project $PROJECT_ID

# View logs for specific agent
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chief_justice" `
    --limit 50 `
    --project $PROJECT_ID
```

### Set Up Monitoring & Alerts
```bash
# Create notification channel (email)
$NOTIFICATION_EMAIL = "your-email@example.com"

gcloud alpha monitoring channels create `
    --display-name="Justice AI Alerts" `
    --type=email `
    --channel-labels email_address=$NOTIFICATION_EMAIL

# Create alert policy for high error rates
gcloud alpha monitoring policies create `
    --notification-channels=<CHANNEL_ID> `
    --display-name="High Error Rate - Justice AI" `
    --condition-display-name="Error Rate > 5%" `
    --condition-threshold-value=0.05

Write-Host "Monitoring and alerts configured!"
```

### Enable Cloud Trace
```bash
# Cloud Trace is automatically enabled for Cloud Run services
# View traces in Google Cloud Console

Write-Host "Cloud Trace is enabled for all services!"
```

---

## Cost Estimation

### Monthly Cost Breakdown (Estimated)

| Service | Usage | Cost |
|---------|-------|------|
| **Cloud Run** | 1M requests, 2GB RAM, 2 vCPU | ~$20-50 |
| **Vertex AI Generative AI (Gemini)** | 500K tokens/day | ~$50-100 |
| **Cloud Storage** | 10GB storage, 1M operations | ~$5-10 |
| **Firestore** | 100K reads, 50K writes daily | ~$15-30 |
| **Cloud Logging** | 100GB logs/month | ~$10-20 |
| **Cloud Monitoring** | Standard monitoring | ~$5 |
| **Artifact Registry** | 5GB storage | ~$2 |
| **Vector Search** | Index hosting | ~$20-50 |
| **Secret Manager** | 6 secrets, 1000 accesses | ~$1 |

**Total Estimated Monthly Cost: $128-266**

### Cost Optimization Tips
- Use **Committed Use Discounts** for Cloud Run
- Set **auto-scaling limits** to prevent runaway costs
- Use **Cloud Run on Compute Engine** for lower costs
- Archive old logs to Cloud Storage
- Use **Firestore on-demand** billing for variable loads

---

## Troubleshooting

### Issue: Service Deployment Failed

**Solution:**
```bash
# Check deployment logs
gcloud run deploy justice-ai-app `
    --image $REGISTRY/justice-ai-app`:latest `
    --region $REGION `
    --debug

# Check service status
gcloud run services describe justice-ai-app --region $REGION
```

### Issue: "Permission Denied" Error

**Solution:**
```bash
# Verify service account has correct roles
gcloud projects get-iam-policy $PROJECT_ID `
    --flatten="bindings[].members" `
    --format="table(bindings.role)" `
    --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT_EMAIL"

# Re-grant roles if needed
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
    --role="roles/aiplatform.admin"
```

### Issue: Cloud Run Container Won't Start

**Solution:**
```bash
# Check container logs
gcloud run logs read justice-ai-app `
    --region $REGION `
    --limit 100

# Verify container runs locally
docker run -it $REGISTRY/justice-ai-app`:latest

# Check Dockerfile for issues
docker build -t test-image ./app --debug
```

### Issue: Vector Search Index Not Found

**Solution:**
```bash
# List all indexes
gcloud ai indexes list --region=$REGION

# Create index if missing
gcloud ai indexes create `
    --display-name="justice-ai-legal-precedents" `
    --region=$REGION

# Populate with data if needed
Write-Host "Populate vector index with legal precedents"
```

### Issue: Gemini API Calls Failing

**Solution:**
```bash
# Verify Generative AI API is enabled
gcloud services list --enabled | Select-String "generativelanguage"

# If not enabled
gcloud services enable generativelanguage.googleapis.com

# Test Gemini connectivity
python -c "from vertexai.generative_models import GenerativeModel; print('Gemini API OK')"
```

---

## Cleanup & Teardown

### Delete All Resources
```bash
# Warning: This will delete everything!

# Delete Cloud Run services
gcloud run services delete justice-ai-app --region=$REGION
gcloud run services delete chief_justice --region=$REGION
# ... repeat for other agents ...

# Delete Storage buckets
gsutil rm -r gs://justice-ai-case-files-$PROJECT_ID
gsutil rm -r gs://justice-ai-reports-$PROJECT_ID
gsutil rm -r gs://justice-ai-legal-docs-$PROJECT_ID

# Delete Firestore
gcloud firestore databases delete --database='(default)'

# Delete Artifact Registry
gcloud artifacts repositories delete justice-ai-repository --location=$REGION

# Delete project (optional)
gcloud projects delete $PROJECT_ID

Write-Host "All resources deleted!"
```

---

## Final Verification

### Post-Deployment Checklist

```bash
# ✅ Verify all services are running
gcloud run services list --platform=managed --region=$REGION

# ✅ Test main app endpoint
curl -X GET "$(gcloud run services describe justice-ai-app --platform managed --region $REGION --format 'value(status.url)')/health"

# ✅ Check Cloud Logging
gcloud logging read "resource.type=cloud_run_revision" --limit 10

# ✅ Verify service accounts
gcloud iam service-accounts list

# ✅ Check enabled APIs
gcloud services list --enabled | Measure-Object

# ✅ Verify storage buckets
gsutil ls -L gs://justice-ai-*

# ✅ Check Firestore
gcloud firestore databases list

Write-Host "All verifications complete! Your Justice AI Workflow is live on Google Cloud! 🎉"
```

---

## Next Steps

1. **Update DNS/Domain** - Point custom domain to Cloud Run URL
2. **Configure SSL/TLS** - Use Cloud Armor for DDoS protection
3. **Set Up CI/CD** - Configure Cloud Build for automated deployments
4. **Add Monitoring Dashboards** - Create custom dashboards in Cloud Monitoring
5. **Schedule Backups** - Set up automated backups for Firestore & Cloud Storage
6. **Document APIs** - Create API documentation for external integrations

---

**🎉 Your Justice AI Workflow is now live on Google Cloud Platform!**

For support and updates: [documentation or contact info]

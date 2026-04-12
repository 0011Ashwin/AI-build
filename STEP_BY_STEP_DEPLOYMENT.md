# Step-by-Step Deployment Guide
## Justice AI Workflow - Phase-Based Deployment

---

## 📋 Overview

This guide shows how to deploy the Justice AI Workflow to Google Cloud Platform **step-by-step using individual deployment phases**. Each phase is independent and can be run separately or all at once.

### Deployment Phases

| Phase | Script | Purpose | Time |
|-------|--------|---------|------|
| **PHASE 1** | `deploy-01-enable-apis.ps1` | Enable 13 required Google Cloud APIs | 3-5 min |
| **PHASE 2** | `deploy-02-setup-database.ps1` | Create Firestore database & Cloud Storage buckets | 5-10 min |
| **PHASE 3** | `deploy-03-deploy-agents.ps1` | Build & deploy 6 agent services one-by-one | 15-20 min |
| **PHASE 4** | `deploy-04-deploy-app.ps1` | Build & deploy main FastAPI application | 5-10 min |

**Total Time**: 30-45 minutes

---

## 🚀 Quick Start (All Phases)

### Option A: Run All Phases Automatically

```powershell
cd d:\Gen-test-02\justice-ai-workflow

# Run all phases sequentially
.\deploy-master.ps1 -ProjectID "your-project-id" -Verbose

# Or without confirmation prompts
.\deploy-master.ps1 -ProjectID "your-project-id" -SkipConfirmation
```

### Option B: Run Individual Phases

Run each phase separately at your own pace:

```powershell
cd d:\Gen-test-02\justice-ai-workflow

# Phase 1: Enable APIs
.\deploy-01-enable-apis.ps1 -ProjectID "your-project-id" -Verbose

# Phase 2: Setup Database
.\deploy-02-setup-database.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose

# Phase 3: Deploy Agents
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose

# Phase 4: Deploy App
.\deploy-04-deploy-app.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose
```

---

## 📖 Detailed Phase Guide

### PHASE 1: Enable Google Cloud APIs

**What it does:**
- Enables 13 required Google Cloud APIs
- Verifies each API is accessible
- Takes 3-5 minutes

**Command:**
```powershell
.\deploy-01-enable-apis.ps1 -ProjectID "your-project-id" -Verbose
```

**APIs Enabled:**
1. Vertex AI Platform
2. Cloud Run
3. Cloud Storage
4. Firestore
5. Cloud Logging
6. Cloud Monitoring
7. Artifact Registry
8. Cloud Build
9. Secret Manager
10. Cloud Container Registry
11. Compute Engine
12. Service Networking
13. Cloud Resource Manager

**What to expect:**
```
✓ Google Cloud SDK found
✓ Google Cloud authentication verified
✓ Project set to: your-project-id
✓ aiplatform is enabled
✓ run is enabled
... (all 13 APIs)
✓ All 13 required APIs have been enabled
```

**Common Issues:**
- **API already enabled**: Safe to ignore - script continues
- **Authentication fails**: Run `gcloud auth login` first
- **Project not found**: Check your project ID is correct

---

### PHASE 2: Setup Database & Storage

**What it does:**
- Creates Firestore NoSQL database (if needed)
- Creates 3 Cloud Storage buckets:
  - `justice-ai-cases-[project-id]` - Case submissions
  - `justice-ai-reports-[project-id]` - Generated reports
  - `justice-ai-legal-docs-[project-id]` - Legal documents for RAG
- Takes 5-10 minutes (Firestore init may take 30-60 seconds)

**Command:**
```powershell
.\deploy-02-setup-database.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose
```

**What to expect:**
```
ℹ Setting project to: your-project-id
✓ Project set to: your-project-id
ℹ Creating Firestore database in us-central1 (Native mode)...
✓ Firestore database created successfully
ℹ Waiting for database to initialize (this takes ~30-60 seconds)...
  [1/3] Creating justice-ai-cases-[project-id]... ✓
  [2/3] Creating justice-ai-reports-[project-id]... ✓
  [3/3] Creating justice-ai-legal-docs-[project-id]... ✓
✓ Cloud Storage buckets created/verified
```

**Firestore Collections (Auto-created):**
- `cases` - Audit case submissions
- `audits` - Audit analysis results
- `legal_precedents` - Legal precedent RAG data
- `case_verdicts` - Agent jury verdicts
- `metrics` - System performance metrics

**Common Issues:**
- **Database already exists**: Safe to skip - reused
- **Buckets already exist**: Safe to skip - reused
- **Firestore timeout**: Normal - wait and proceed to next phase

---

### PHASE 3: Deploy Agents One-by-One

**What it does:**
- Sets up service account with required IAM roles
- Configures Artifact Registry (Docker repository)
- Builds 6 agent Docker images
- Pushes images to Artifact Registry
- Deploys each agent to Cloud Run individually
- Takes 15-20 minutes

**Command:**
```powershell
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose
```

**Agents Deployed:**
1. **Chief Justice** (Port 8000) - Root orchestrator
2. **Quantitative Auditor** (Port 8001) - Bias analysis
3. **Legal Researcher** (Port 8002) - Legal precedent RAG
4. **Mitigator Juror** (Port 8003) - Defense advocate
5. **Strict Auditor Juror** (Port 8004) - Prosecution advocate
6. **Ethicist Juror** (Port 8005) - Ethics evaluator

**What to expect:**
```
✓ Google Cloud SDK found
✓ Docker found
✓ Project configured

  ▶ [1/6] Building chief-justice
✓ Image built successfully

  ▶ [1/6] Pushing chief-justice
✓ Image pushed successfully

  ▶ [1/6] Deploying chief-justice to Cloud Run
  Starting deployment...
✓ Deployment completed
    Service URL: https://chief-justice-xxxxx.run.app

(... repeats for remaining 5 agents ...)

✓ All agents deployed successfully
```

**Cloud Run Configuration per Agent:**
- Memory: 2GB
- CPU: 2 vCPU
- Timeout: 3600 seconds
- Max Concurrency: 80
- Authentication: Service account

**Monitoring Agent Deployment:**
```powershell
# Check agent services
gcloud run services list --project=your-project-id

# View agent logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=chief-justice' -n 10 --project=your-project-id

# Get specific agent URL
gcloud run services describe chief-justice --region=us-central1 --format="value(status.url)" --project=your-project-id
```

---

### PHASE 4: Deploy Main Application

**What it does:**
- Builds FastAPI application Docker image
- Pushes image to Artifact Registry
- Deploys to Cloud Run with higher resources
- Verifies deployment and performs health check
- Takes 5-10 minutes

**Command:**
```powershell
.\deploy-04-deploy-app.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose
```

**Application Configuration:**
- Service Name: `justice-ai-app`
- Memory: 4GB (higher for orchestration)
- CPU: 4 vCPU
- Timeout: 3600 seconds
- Max Concurrency: 100
- Frontend Port: 8080 (internal), 443 (HTTPS external)

**What to expect:**
```
✓ Google Cloud SDK found
✓ Docker found
✓ Project configured

ℹ Building application Docker image...
✓ Application image built successfully

ℹ Pushing application image to registry...
✓ Application image pushed successfully

ℹ Deploying service...
  Starting Cloud Run deployment (this may take 2-3 minutes)...
✓ Application deployment completed successfully

🌐 Application URL:
    https://justice-ai-app-xxxxx.run.app

ℹ Testing health endpoint...
✓ Health check passed - Application is running
```

**Access Your Application:**
```
Frontend: https://justice-ai-app-xxxxx.run.app
Health Check: https://justice-ai-app-xxxxx.run.app/health
API Docs: https://justice-ai-app-xxxxx.run.app/docs (Swagger)
```

---

## 🔄 Advanced Scenarios

### Scenario 1: Deploy Only Agents

```powershell
# Skip to agent deployment after database is ready
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose
```

### Scenario 2: Deploy Specific Agent

```powershell
# Deploy only the legal researcher agent
.\deploy-03-deploy-agents.ps1 `
    -ProjectID "your-project-id" `
    -Region "us-central1" `
    -DeployAgent "legal-researcher" `
    -Verbose
```

### Scenario 3: Different Region

```powershell
# Deploy to europe-west1 instead of us-central1
.\deploy-master.ps1 `
    -ProjectID "your-project-id" `
    -Region "europe-west1" `
    -Verbose
```

### Scenario 4: Skip Database Setup

```powershell
# Run only APIs and app (database already exists)
.\deploy-master.ps1 `
    -ProjectID "your-project-id" `
    -Phase "apis" `
    -Verbose

.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -Verbose
.\deploy-04-deploy-app.ps1 -ProjectID "your-project-id" -Verbose
```

---

## 📊 Monitoring Deployment

### View Deployment Status

```powershell
# List all deployed services
gcloud run services list --project=your-project-id

# Get specific service details
gcloud run services describe justice-ai-app --region=us-central1 --project=your-project-id

# View deployment revisions
gcloud run services describe justice-ai-app --region=us-central1 --format=json --project=your-project-id | ConvertFrom-Json
```

### View Logs

```powershell
# View application logs
gcloud logging read 'resource.type=cloud_run_revision' `
    --limit=100 `
    --project=your-project-id

# Follow logs in real-time (requires Cloud Logging API)
gcloud logging read 'severity>=DEFAULT' --project=your-project-id --format json

# View errors only
gcloud logging read 'severity=ERROR' --limit=50 --project=your-project-id
```

### Monitor Performance

```powershell
# View metrics in Cloud Console
# https://console.cloud.google.com/monitoring/dashboards?project=your-project-id

# Get memory usage
gcloud monitoring time-series list \
    --filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/task_executions"' \
    --project=your-project-id
```

---

## ✅ Post-Deployment Checklist

After all phases are complete:

- [ ] Access application frontend at provided URL
- [ ] Verify health endpoint responds (status 200)
- [ ] Check Cloud Console shows all 7 services
- [ ] Test case submission in UI
- [ ] Verify audit workflow executes
- [ ] Check generated reports in Cloud Storage
- [ ] Review logs for any errors
- [ ] Set up monitoring alerts (optional)
- [ ] Configure custom domain (optional)
- [ ] Set up backups (optional)

---

## 🐛 Troubleshooting

### Phase 1 Issues

**Problem**: "APIs failed to enable"
```powershell
# Solution: Try enabling manually
gcloud services enable aiplatform.googleapis.com --project=your-project-id
```

**Problem**: "Authentication not found"
```powershell
# Solution: Login to Google Cloud
gcloud auth login
gcloud auth application-default login
```

### Phase 2 Issues

**Problem**: "Firestore database already exists"
```powershell
# Solution: This is normal - script skips creation
# Existing database will be reused
```

**Problem**: "Failed to create Cloud Storage buckets"
```powershell
# Solution: Check bucket name uniqueness (must be globally unique)
# Try with different project ID suffix
```

### Phase 3 Issues

**Problem**: "Docker build fails"
```powershell
# Solution: Ensure Docker Desktop is running
docker --version
docker ps
```

**Problem**: "Artifact Registry authentication fails"
```powershell
# Solution: Reconfigure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

**Problem**: "Cloud Run deployment timeout"
```powershell
# Solution: Wait a few minutes and check status
gcloud run services describe agent-name --region=us-central1
```

### Phase 4 Issues

**Problem**: "Application health check fails"
```powershell
# Solution: Wait 30-60 seconds for initialization
# Health endpoint becomes available after about 1 minute
```

**Problem**: "Can't reach application URL"
```powershell
# Solution: Check if service is public
# View in Cloud Console to verify "Allow unauthenticated" is set
```

---

## 📝 Deployment Log Locations

All deployment phases create detailed logs:

```
Phase 1 Log: Terminal output from deploy-01-enable-apis.ps1
Phase 2 Log: Terminal output from deploy-02-setup-database.ps1
Phase 3 Log: Terminal output from deploy-03-deploy-agents.ps1
Phase 4 Log: Terminal output from deploy-04-deploy-app.ps1
```

Save logs for troubleshooting:
```powershell
# Run with output redirection
.\deploy-master.ps1 -ProjectID "your-project-id" | Tee-Object -FilePath "deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
```

---

## 💰 Cost Management

**Estimated Monthly Cost**: $120-185

**Cost Breakdown:**
- Cloud Run (7 services, 8 hours/day): $60-80
- Firestore operations: $30-40
- Cloud Storage (1GB data): $5-10
- Vertex AI API calls: $20-30
- Logging & Monitoring: $5-10

**Optimize Costs:**
```powershell
# Delete unused services
gcloud run services delete service-name --region=us-central1

# Set resource limits
gcloud run deploy service-name --memory 512Mi --cpu 0.5

# Schedule service shutdowns (requires Cloud Scheduler)
```

---

## 🎯 Next Steps

After successful deployment:

1. **Access Application**: Navigate to the provided HTTPS URL
2. **Submit Test Cases**: Use the web interface to submit bias audit cases
3. **Monitor Workflow**: Watch agents collaborate in real-time
4. **Review Reports**: Download generated audit reports
5. **Set Up Monitoring**: Configure alerts in Cloud Console
6. **Customize Agents**: Modify agent instructions in source code
7. **Scale as Needed**: Increase Cloud Run resources as needed

---

## 📞 Support Commands

```powershell
# View all deployed services
gcloud run services list --project=your-project-id

# Get application URL
gcloud run services describe justice-ai-app --region=us-central1 --format="value(status.url)"

# View real-time logs
gcloud logging read --limit=50 --follow --project=your-project-id

# Clean up (delete services)
gcloud run services delete justice-ai-app --region=us-central1 --quiet

# View project costs (requires Billing API)
gcloud billing accounts list
```

---

**Happy Deploying! 🚀**

For issues or questions, check the comprehensive documentation:
- QUICK_CLOUD_SETUP.md - Executive summary
- CLOUD_DEPLOYMENT_GUIDE.md - Complete setup reference
- DEPLOYMENT_AUTOMATION_GUIDE.md - Detailed manual steps
- VERTEX_AI_SERVICES_GUIDE.md - API integration details

# Deployment Scripts Index
## Justice AI Workflow - Phase-Based Deployment

---

## 📦 What's New: 4-Phase Deployment System

We've restructured the deployment into **4 independent phases** that run sequentially. Each phase is a standalone PowerShell script that can be run individually or together.

### New Scripts Created

| Script | Purpose | Run Time |
|--------|---------|----------|
| `deploy-01-enable-apis.ps1` | Enable 13 required Google Cloud APIs | 3-5 min |
| `deploy-02-setup-database.ps1` | Create Firestore database & Cloud Storage buckets | 5-10 min |
| `deploy-03-deploy-agents.ps1` | Build & deploy 6 agent services one-by-one | 15-20 min |
| `deploy-04-deploy-app.ps1` | Build & deploy main FastAPI application | 5-10 min |
| `deploy-master.ps1` | Orchestrator - runs all phases or specific phase | 30-45 min |

### New Documentation

| Document | Purpose |
|----------|---------|
| `STEP_BY_STEP_DEPLOYMENT.md` | Complete guide to phase-based deployment |
| This file | Quick reference index |

---

## 🚀 Quick Start

### Option 1: Run Everything (Recommended for first deployment)

```powershell
cd d:\Gen-test-02\justice-ai-workflow

# Run all phases with confirmation
.\deploy-master.ps1 -ProjectID "your-project-id" -Verbose

# Or skip confirmation
.\deploy-master.ps1 -ProjectID "your-project-id" -SkipConfirmation
```

**Total time: 30-45 minutes**

---

### Option 2: Run Phases One-by-One (More Control)

Run at your own pace with full control over each phase:

```powershell
cd d:\Gen-test-02\justice-ai-workflow

# ============ PHASE 1: Enable APIs ============
# Time: 3-5 minutes
.\deploy-01-enable-apis.ps1 -ProjectID "your-project-id" -Verbose

# [Wait for completion, then run Phase 2]

# ============ PHASE 2: Setup Database ============
# Time: 5-10 minutes
.\deploy-02-setup-database.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose

# [Wait for completion, then run Phase 3]

# ============ PHASE 3: Deploy Agents ============
# Time: 15-20 minutes
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose

# [Wait for completion, then run Phase 4]

# ============ PHASE 4: Deploy Application ============
# Time: 5-10 minutes
.\deploy-04-deploy-app.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose
```

---

## 📖 Phase Details

### PHASE 1: Enable APIs (3-5 minutes)

**What**: Enables 13 required Google Cloud APIs on your project

**Enables**:
- Vertex AI Platform (for Gemini models)
- Cloud Run (for microservices)
- Firestore (database)
- Cloud Storage (object storage)
- Cloud Logging & Monitoring
- Artifact Registry (Docker images)
- Cloud Build (CI/CD)
- And 6 more supporting services

**Run**:
```powershell
.\deploy-01-enable-apis.ps1 -ProjectID "your-project-id" -Verbose
```

---

### PHASE 2: Setup Database & Storage (5-10 minutes)

**What**: Creates database and storage infrastructure

**Creates**:
- **Firestore Database** (NoSQL) in us-central1
  - Collections: cases, audits, legal_precedents, case_verdicts, metrics
- **Cloud Storage Buckets** (3 total):
  - `justice-ai-cases-[project-id]` - Case submissions
  - `justice-ai-reports-[project-id]` - Generated reports
  - `justice-ai-legal-docs-[project-id]` - Legal documents

**Run**:
```powershell
.\deploy-02-setup-database.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose
```

---

### PHASE 3: Deploy Agents (15-20 minutes)

**What**: Builds and deploys 6 AI agents to Cloud Run

**Deploys** (one-by-one):
1. Chief Justice (Orchestrator)
2. Quantitative Auditor (Bias analysis)
3. Legal Researcher (RAG)
4. Mitigator Juror (Defense)
5. Strict Auditor Juror (Prosecution)
6. Ethicist Juror (Ethics)

**Each agent gets**:
- 2GB RAM, 2 vCPU
- 3600s timeout
- Service account authentication

**Run**:
```powershell
# Deploy all agents
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose

# Or deploy specific agent
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -DeployAgent "legal-researcher" -Verbose
```

---

### PHASE 4: Deploy Application (5-10 minutes)

**What**: Builds and deploys main FastAPI application

**Deploys**:
- FastAPI server with orchestration logic
- Frontend (HTML/CSS/JavaScript)
- Agent coordination layer
- Workflow state management

**Application gets**:
- 4GB RAM, 4 vCPU (higher for orchestration)
- 3600s timeout
- Public HTTPS endpoint

**Run**:
```powershell
.\deploy-04-deploy-app.ps1 -ProjectID "your-project-id" -Region "us-central1" -Verbose
```

**After deployment**:
- Access at: `https://justice-ai-app-[random].run.app`
- Health check: `https://justice-ai-app-[random].run.app/health`

---

## 🎯 Master Orchestrator

The `deploy-master.ps1` script can run:

- **All phases**: `deploy-master.ps1 -Phase "all"`
- **Just APIs**: `deploy-master.ps1 -Phase "apis"`
- **Just database**: `deploy-master.ps1 -Phase "database"`
- **Just agents**: `deploy-master.ps1 -Phase "agents"`
- **Just app**: `deploy-master.ps1 -Phase "app"`

**Example**: Run only APIs and then skip to agents

```powershell
# Enable APIs
.\deploy-master.ps1 -ProjectID "your-project-id" -Phase "apis"

# Later... deploy agents (skip database if already done)
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id"
```

---

## 📋 Execution Flow

```
Phase 1: Enable APIs
    ↓ (APIs are now active)
Phase 2: Setup Database
    ↓ (Firestore + Storage ready)
Phase 3: Deploy Agents (one-by-one)
    ├─ Chief Justice
    ├─ Quantitative Auditor
    ├─ Legal Researcher
    ├─ Mitigator Juror
    ├─ Strict Auditor Juror
    └─ Ethicist Juror
    ↓ (All agents running)
Phase 4: Deploy App
    ↓ (All 7 services deployed)
✅ System Ready
```

---

## 🔍 What Happens in Each Phase

### Phase 1 Process
1. Validates Google Cloud SDK installation
2. Checks authentication
3. Sets project ID
4. Iterates through 13 APIs
5. Enables each API
6. Verifies all APIs are active

### Phase 2 Process
1. Checks/creates Firestore database
2. Initializes Firestore collections
3. Creates 3 Cloud Storage buckets
4. Verifies storage setup
5. Ready for agent deployment

### Phase 3 Process
1. Creates service account with IAM roles
2. Sets up Artifact Registry
3. Configures Docker authentication
4. **For each agent (1-6)**:
   - Builds Docker image
   - Pushes to Artifact Registry
   - Deploys to Cloud Run
   - Verifies deployment
5. All 6 agents running

### Phase 4 Process
1. Builds main app Docker image
2. Pushes to Artifact Registry
3. Deploys to Cloud Run
4. Performs health check
5. Application ready

---

## 📊 Timeline Example

```
11:00 - Start Phase 1: Enable APIs (3 min)
        Active: APIs enabled ✓
11:03 - Start Phase 2: Setup Database (10 min)
        Active: APIs + Database ✓
11:13 - Start Phase 3: Deploy Agents (20 min)
        Active: All agents deployed ✓
11:33 - Start Phase 4: Deploy App (10 min)
        Active: All 7 services + App deployed ✓
11:43 - Complete! ✓
```

---

## ✅ Pre-Deployment Checklist

Before running any deployment script:

- [ ] Have Google Cloud account (sign up if needed)
- [ ] Have valid GCP project (create if needed)
- [ ] Billing enabled on project
- [ ] Google Cloud SDK installed (`gcloud --version`)
- [ ] Authenticated to Google Cloud (`gcloud auth login`)
- [ ] Docker Desktop installed and running
- [ ] PowerShell 7+ installed
- [ ] Know your GCP project ID
- [ ] Choose a region (default: us-central1)

---

## 🆗 Environment Variables (Optional)

Set these to avoid typing parameters:

```powershell
# Windows PowerShell
$env:GCP_PROJECT_ID = "your-project-id"
$env:GCP_REGION = "us-central1"

# Then run with fewer parameters
.\deploy-master.ps1
```

---

## 📈 Monitoring Deployment

Watch what's happening:

```powershell
# View services being deployed
gcloud run services list --project=your-project-id

# Watch logs in real-time
gcloud logging read --follow --limit=50 --project=your-project-id

# Check specific service status
gcloud run services describe justice-ai-app --region=us-central1 --project=your-project-id
```

---

## 🛑 If Something Goes Wrong

**Phase fails?** Each phase is independent - try again:

```powershell
# If Phase 3 fails, just re-run it
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -Verbose

# It will skip what's already done and continue
```

**Need to see details?** Add `-Verbose`:

```powershell
# Shows detailed output
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -Verbose
```

**Need to debug?** Check logs:

```powershell
# View all errors on project
gcloud logging read 'severity=ERROR' --limit=50 --project=your-project-id

# View specific service logs
gcloud logging read 'resource.labels.service_name=chief-justice' --limit=50 --project=your-project-id
```

---

## 🧹 Cleanup

If you need to stop/delete services:

```powershell
# Delete specific service
gcloud run services delete justice-ai-app --region=us-central1 --quiet --project=your-project-id

# Delete all services
gcloud run services delete chief-justice quantitative-auditor legal-researcher mitigator-juror strict-auditor-juror ethicist-juror justice-ai-app --region=us-central1 --quiet --project=your-project-id

# Disable APIs (optional)
gcloud services disable aiplatform.googleapis.com --project=your-project-id
```

---

## 📚 Full Documentation

For complete details, see:

- **[STEP_BY_STEP_DEPLOYMENT.md](STEP_BY_STEP_DEPLOYMENT.md)** - Comprehensive guide with troubleshooting
- **[QUICK_CLOUD_SETUP.md](QUICK_CLOUD_SETUP.md)** - Executive summary
- **[CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md)** - Complete GCP reference
- **[DEPLOYMENT_AUTOMATION_GUIDE.md](DEPLOYMENT_AUTOMATION_GUIDE.md)** - Detailed manual setup
- **[VERTEX_AI_SERVICES_GUIDE.md](VERTEX_AI_SERVICES_GUIDE.md)** - API integration details

---

## 🚀 Ready to Deploy?

```powershell
# Get started with one command!
cd d:\Gen-test-02\justice-ai-workflow
.\deploy-master.ps1 -ProjectID "your-project-id" -Verbose
```

Sit back and watch your AI agents deploy! ✨

---

**Questions?** Check [STEP_BY_STEP_DEPLOYMENT.md](STEP_BY_STEP_DEPLOYMENT.md) for detailed troubleshooting and advanced scenarios.

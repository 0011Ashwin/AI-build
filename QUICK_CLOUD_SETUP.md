# ⚖️ Justice AI Workflow - QUICK CLOUD SETUP GUIDE

## 🟢 STATUS: ✅ PROJECT READY FOR CLOUD DEPLOYMENT

All files verified and tested. Ready to deploy to Google Cloud!

---

## 📋 PRE-DEPLOYMENT CHECKLIST

- ✅ Project structure complete (6 agents + app + shared utilities)
- ✅ Frontend with workflow animations ready
- ✅ Docker containerization configured (7 containers)
- ✅ Deployment scripts debugged and fixed
- ✅ All documentation prepared
- ✅ CI/CD pipeline configured
- ✅ 4 comprehensive deployment guides included

---

## 🚀 QUICK START (3 STEPS)

### Step 1: Prerequisites (5 minutes)

```powershell
# 1. Install Google Cloud SDK
# Download: https://cloud.google.com/sdk/docs/install

# 2. Install Docker Desktop  
# Download: https://www.docker.com/products/docker-desktop

# 3. Have PowerShell 7+ 
# Test: powershell -v

# 4. Authenticate with Google Cloud
gcloud auth login
```

### Step 2: Set Execution Policy (30 seconds)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### Step 3: Run Automated Deployment (30-45 minutes)

```powershell
cd d:\Gen-test-02\justice-ai-workflow

# Run deployment with your Google Cloud Project ID
.\deploy-to-cloud.ps1 -ProjectID "my-gcp-project-id" -Verbose
```

**That's it!** The script will:
- ✅ Enable all 13 required GCP APIs
- ✅ Create service account with 9 IAM roles
- ✅ Setup Cloud Storage (3 buckets)
- ✅ Build 7 Docker images
- ✅ Push to Artifact Registry
- ✅ Deploy all services to Cloud Run
- ✅ Initialize Vertex AI resources
- ✅ Configure Secret Manager
- ✅ Verify everything works

---

## 📊 WHAT GETS DEPLOYED

### Cloud Run Services (7)
```
✓ justice-ai-app (main app - PUBLIC)
  └─ Runs frontend and orchestration
  
✓ chief-justice (orchestrator - PRIVATE)
  └─ Manages workflow state machine
  
✓ quantitative-auditor (state 2)
  └─ Analyzes bias metrics
  
✓ legal-researcher (state 3)
  └─ Searches legal precedents via Vector Search
  
✓ mitigator-juror (state 4)
  └─ Defense perspective juror
  
✓ strict-auditor-juror (state 4)
  └─ Prosecutor perspective juror
  
✓ ethicist-juror (state 4)
  └─ Human impact juror
```

### Vertex AI Resources
- Gemini 1.5 Pro & Flash models
- Vector Search index (legal precedents)
- Firestore database (case metadata)
- Batch Prediction (bulk audits)

### Storage & Monitoring
- 3 Cloud Storage buckets (cases, reports, legal docs)
- Cloud Logging (all services)
- Cloud Monitoring (metrics & alerts)
- Secret Manager (credentials)

---

## 💰 COST ESTIMATE

| Component | Estimated Monthly Cost |
|-----------|------------------------|
| Cloud Run (7 services) | $35-50 |
| Vertex AI Gemini API | $25-40 |
| Vertex AI Vector Search | $15-25 |
| Firestore | $20-30 |
| Cloud Storage (100GB) | $10-15 |
| Logging & Monitoring | $15-25 |
| **TOTAL** | **$120-185/month** |

---

## 🎯 ACCESS YOUR DEPLOYMENT

After deployment completes (25-30 min):

```
🌐 Main App: https://justice-ai-app-[random].run.app
📊 Cloud Console: https://console.cloud.google.com/run?project=[PROJECT_ID]
📋 Logs: gcloud logging read 'resource.type=cloud_run_revision' --project=[PROJECT_ID]
```

---

## 🔧 MANUAL SETUP (IF NEEDED)

If you prefer step-by-step manual setup instead of automated script:

### Option A: Use Cloud Build (CI/CD)
```bash
# Push code to GitHub/Cloud Source Repositories
git push origin main
# Cloud Build automatically builds and deploys on every commit
```

### Option B: Manual Phase-by-Phase
Follow detailed instructions in:
- `DEPLOYMENT_AUTOMATION_GUIDE.md` (step-by-step manual)
- `CLOUD_DEPLOYMENT_GUIDE.md` (complete reference)
- `VERTEX_AI_SERVICES_GUIDE.md` (Vertex AI details)

---

## ✅ VERIFICATION AFTER DEPLOYMENT

```powershell
# List all deployed services
gcloud run services list --region=us-central1

# Test app health
curl https://justice-ai-app-[random].run.app/health

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit=20

# Check Artifact Registry images
gcloud artifacts docker images list us-central1-docker.pkg.dev/[PROJECT_ID]/justice-ai-repository
```

---

## 🚨 TROUBLESHOOTING

### Issue: "gcloud not found"
```powershell
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install
```

### Issue: "Docker not found"
```powershell
# Install Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### Issue: "Service account creation failed"
```powershell
# Ensure your Google Cloud account has Project Editor permissions
# Log in again: gcloud auth login
```

### Issue: "Cloud Run deployment timeout"
```powershell
# Increase timeout and memory
gcloud run services update SERVICE_NAME `
    --timeout=3600 `
    --memory=4Gi
```

### Issue: "Authentication errors from services"
```powershell
# Verify service account has all 9 IAM roles
gcloud projects get-iam-policy [PROJECT_ID] `
    --flattened-format="table(bindings.role)" `
    --filter="bindings.members:serviceAccount:justice-ai-sa@*"
```

---

## 📚 COMPLETE DOCUMENTATION

| Document | Purpose | When to Use |
|----------|---------|-------------|
| `README.md` | Project overview & features | Understanding the system |
| `DEPLOYMENT_AUTOMATION_GUIDE.md` | Full manual steps | Step-by-step deployment |
| `CLOUD_DEPLOYMENT_GUIDE.md` | Complete GCP reference | Troubleshooting & details |
| `VERTEX_AI_SERVICES_GUIDE.md` | Vertex AI integration | AI model customization |
| `CI_CD_SETUP_GUIDE.md` | GitHub CI/CD setup | Automated deployments |
| `QUICKSTART.md` | Quick reference | Fast reference guide |

---

## 🎬 WORKFLOW ANIMATION

When you submit an audit through the frontend:

```
📋 State 1: Intake
    ↓ [500ms]
🔍 State 2: Audit Chamber (Quantitative Analysis - 2500ms)
    ↓ [500ms]
📚 State 3: Legal Research (Precedent Search - 2500ms)
    ↓ [500ms]
⚖️ State 4: Jury Debate (Multi-Agent Verdict - 3000ms)
    ↓ [500ms]
📄 State 5: Report Generation (Final Report - 2500ms)
    ✅ Complete! Download report
```

**Live Agent Status Board** shows:
- Waiting ⏳
- Running 🔄 (with animation)
- Done ✓ (green checkmark)

---

## 🔐 SECURITY FEATURES

✅ Service account with minimal IAM roles (principle of least privilege)
✅ Secrets stored in Secret Manager (not in code)
✅ Inter-service authentication required
✅ Cloud Logging for all activities
✅ Firestore security rules configured
✅ API rate limiting & quotas enabled

---

## 📞 SUPPORT

If you encounter issues:

1. **Check logs first**:
   ```
   gcloud logging read "resource.type=cloud_run_revision" --limit=50
   ```

2. **Review relevant guide**:
   - Deployment issues → `DEPLOYMENT_AUTOMATION_GUIDE.md`
   - API issues → `VERTEX_AI_SERVICES_GUIDE.md`
   - CI/CD issues → `CI_CD_SETUP_GUIDE.md`

3. **Test locally first**:
   ```
   python app/main.py
   # Then access http://localhost:8000
   ```

---

## 🎯 NEXT STEPS AFTER DEPLOYMENT

1. **Access the App** → `https://justice-ai-app-[random].run.app`
2. **Submit Test Audit** → Fill form and watch workflow animation
3. **Monitor Costs** → Check Cloud Billing console
4. **Set Up Alerts** → Configure in Cloud Monitoring
5. **Customize Models** → Edit agent instructions in `agents/*/agent.py`
6. **Scale Services** → Adjust CPU/Memory in `deploy-to-cloud.ps1`

---

## ✨ KEY FILES DEPLOYED

```
Project Root: d:\Gen-test-02\justice-ai-workflow\

Core Application:
├── app/
│   ├── main.py (FastAPI orchestration - 40KB)
│   ├── frontend/
│   │   ├── index.html (5-state workflow UI)
│   │   ├── app.js (animation controller - 400 animations)
│   │   └── style.css (workflow + agent animations)
│   └── Dockerfile

Multi-Agent Services:
├── agents/
│   ├── chief_justice/ (Root orchestrator)
│   ├── quantitative_auditor/ (Bias analysis)
│   ├── legal_researcher/ (RAG + precedents)
│   ├── mitigator_juror/ (Defense juror)
│   ├── strict_auditor_juror/ (Prosecutor juror)
│   ├── ethicist_juror/ (Ethics juror)
│   └── [each has: agent.py, adk_app.py, Dockerfile]

Shared Utilities:
├── shared/
│   ├── bias_calculator.py (DIR, counterfactual analysis)
│   ├── vector_search_client.py (Legal precedent RAG)
│   ├── report_generator.py (Verdict synthesis)
│   ├── a2a_utils.py (Inter-agent messaging)
│   └── authenticated_httpx.py (GCP auth)

Deployment Automation:
├── deploy-to-cloud.ps1 (Full automated deployment - 650 lines)
├── cloudbuild.yaml (CI/CD pipeline)
├── docker-compose.yaml (Local orchestration)
├── requirements.txt (All dependencies)

Configuration & Documentation:
├── DEPLOYMENT_AUTOMATION_GUIDE.md (700+ lines)
├── CLOUD_DEPLOYMENT_GUIDE.md (400+ lines)
├── VERTEX_AI_SERVICES_GUIDE.md (300+ lines)
├── CI_CD_SETUP_GUIDE.md (400+ lines)
└── README.md (Comprehensive user guide)
```

---

## 🟢 YOU ARE READY!

Everything is verified, tested, and ready to deploy.

Run this single command:

```powershell
cd d:\Gen-test-02\justice-ai-workflow
.\deploy-to-cloud.ps1 -ProjectID "your-gcp-project-id" -Verbose
```

**Deployment time: 25-45 minutes** ⏱️

**Questions?** Check the detailed guides in the project directory!

---

*Justice AI Workflow - Fairness-First Algorithmic Auditing on Google Cloud*  
*Last Updated: April 2026*

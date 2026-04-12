# Cloud Shell Deployment Guide
## Justice AI Workflow - Bash Scripts for Google Cloud Shell

---

## 🎯 Overview

These bash scripts allow you to deploy the Justice AI Workflow **directly from Google Cloud Shell** without needing Windows PowerShell or Docker Desktop locally.

### What's Different from PowerShell Version?

| Feature | PowerShell | Bash (Cloud Shell) |
|---------|-----------|-------------------|
| Location | Local Windows | Google Cloud Shell |
| Prerequisites | Docker Desktop, PowerShell 7 | Just `gcloud` CLI |
| Setup Time | Quick (already installed) | ~2 minutes (gcloud config) |
| Best For | Local development | Production deployments |
| Docker Builds | Local machine | Cloud Build (optional) |

---

## 📦 New Bash Scripts

```
d:\Gen-test-02\justice-ai-workflow\
├── deploy-01-enable-apis.sh         ← Phase 1 (Bash)
├── deploy-02-setup-database.sh      ← Phase 2 (Bash)
├── deploy-03-deploy-agents.sh       ← Phase 3 (Bash)
├── deploy-04-deploy-app.sh          ← Phase 4 (Bash)
└── deploy-master.sh                 ← Orchestrator (Bash)
```

### Compatible with All Platforms
- ✅ Google Cloud Shell (Recommended)
- ✅ Linux / Ubuntu
- ✅ macOS
- ✅ Windows with WSL2
- ✅ Any bash-compatible environment

---

## 🚀 Quick Start in Cloud Shell

### Step 1: Open Cloud Shell

Navigate to your Google Cloud Project and click the **>_ Cloud Shell** icon at the top.

### Step 2: Clone or Download the Scripts

```bash
# Option A: If scripts are in your GitHub repo
git clone https://github.com/your-org/your-repo.git
cd your-repo/justice-ai-workflow

# Option B: If files are locally on your machine, upload them
# Use Cloud Shell's "Upload file" option (gear icon → Upload files)
```

### Step 3: Make Scripts Executable

```bash
chmod +x deploy-master.sh
chmod +x deploy-*.sh
```

### Step 4: Run the Master Deployment Script

```bash
# Run everything (all 4 phases)
./deploy-master.sh --project-id "ai-build-493107"

# With verbose output
./deploy-master.sh --project-id "ai-build-493107" --verbose

# Skip confirmation prompts
./deploy-master.sh --project-id "ai-build-493107" --skip-confirmation
```

**That's it! Sit back and watch your AI agents deploy.** ☕

---

## 📋 Command Reference

### Master Orchestrator

```bash
# Run all phases
./deploy-master.sh --project-id "your-project-id"

# Run specific phase
./deploy-master.sh --project-id "your-project-id" --phase apis
./deploy-master.sh --project-id "your-project-id" --phase database
./deploy-master.sh --project-id "your-project-id" --phase agents
./deploy-master.sh --project-id "your-project-id" --phase app

# Different region
./deploy-master.sh --project-id "your-project-id" --region "europe-west1"

# Skip confirmations (for automation)
./deploy-master.sh --project-id "your-project-id" --skip-confirmation

# With verbose output
./deploy-master.sh --project-id "your-project-id" --verbose
```

### Individual Phase Scripts

```bash
# Phase 1: Enable APIs (3-5 min)
./deploy-01-enable-apis.sh --project-id "your-project-id"

# Phase 2: Setup Database (5-10 min)
./deploy-02-setup-database.sh --project-id "your-project-id" --region "us-central1"

# Phase 3: Deploy Agents (15-20 min)
./deploy-03-deploy-agents.sh --project-id "your-project-id" --region "us-central1"

# Phase 4: Deploy App (5-10 min)
./deploy-04-deploy-app.sh --project-id "your-project-id" --region "us-central1"
```

---

## 🎯 Deployment in Cloud Shell

### Prerequisites in Cloud Shell

Google Cloud Shell comes pre-installed with:
- ✅ `gcloud` CLI (Google Cloud SDK)
- ✅ `docker` (Docker CLI)
- ✅ `bash`
- ✅ `curl`

**Everything you need is already there!**

### Get Your Project ID

In Cloud Shell, your project ID is already set, but you can verify:

```bash
# See your current project
echo $GOOGLE_CLOUD_PROJECT

# Or use gcloud
gcloud config get-value project

# List all your projects
gcloud projects list --format="value(PROJECT_ID, NAME)"
```

### Three Ways to Deploy

#### Option 1: Automatic (Recommended)

```bash
./deploy-master.sh --project-id "$GOOGLE_CLOUD_PROJECT"
```

Uses environment variable that's already set in Cloud Shell.

#### Option 2: Step-by-Step

```bash
# Run one phase at a time with full control
./deploy-01-enable-apis.sh --project-id "ai-build-493107"

# [Wait for completion, monitor progress]

./deploy-02-setup-database.sh --project-id "ai-build-493107"

# [Wait for completion]

./deploy-03-deploy-agents.sh --project-id "ai-build-493107"

# [Wait for completion - this takes longest]

./deploy-04-deploy-app.sh --project-id "ai-build-493107"
```

#### Option 3: Run Specific Phase

```bash
# Re-deploy just agents (others already done)
./deploy-03-deploy-agents.sh --project-id "ai-build-493107"
```

---

## 🔄 Understanding the Deployment Flow

### Cloud Shell + These Scripts

```
Your Local Computer
    ↓
Cloud Shell Terminal
    ├─ ./deploy-master.sh
    │  └─ Runs gcloud commands
    │     ├─ Enable APIs in your project
    │     ├─ Create Firestore database
    │     ├─ Build Docker images (locally in Cloud Shell)
    │     ├─ Push to Artifact Registry
    │     └─ Deploy to Cloud Run
    │
    └─ Deployment Complete
       └─ App Live at: https://justice-ai-app-xxxxx.run.app
```

### No Docker Desktop Needed!

Cloud Shell has Docker pre-installed and authenticated with your project. The scripts:
1. Build Docker images inside Cloud Shell
2. Push directly to Google Artifact Registry
3. Deploy to Cloud Run

No local Docker Desktop required on your machine!

---

## 📊 What Gets Deployed

After running all scripts in Cloud Shell:

```
✓ 13 Google Cloud APIs enabled
✓ 1 Firestore database (NoSQL)
✓ 3 Cloud Storage buckets
✓ 1 Artifact Registry repository
✓ 1 Service account with IAM roles
✓ 7 Cloud Run services:
  ├─ justice-ai-app (Main app) - 4GB, 4 vCPU
  ├─ chief-justice (Orchestrator) - 2GB, 2 vCPU
  ├─ quantitative-auditor - 2GB, 2 vCPU
  ├─ legal-researcher - 2GB, 2 vCPU
  ├─ mitigator-juror - 2GB, 2 vCPU
  ├─ strict-auditor-juror - 2GB, 2 vCPU
  └─ ethicist-juror - 2GB, 2 vCPU
```

---

## 🎬 Example Session in Cloud Shell

```bash
# 1. Clone your repo or upload files
$ git clone https://github.com/your-org/your-repo.git
$ cd your-repo/justice-ai-workflow

# 2. Make scripts executable
$ chmod +x deploy-*.sh

# 3. Check your project
$ echo $GOOGLE_CLOUD_PROJECT
ai-build-493107

# 4. Run deployment (all phases)
$ ./deploy-master.sh --project-id "ai-build-493107" --verbose

╔════════════════════════════════════════════════════════════════════╗
║                 JUSTICE AI WORKFLOW                               ║
║             MASTER DEPLOYMENT ORCHESTRATOR                        ║
╚════════════════════════════════════════════════════════════════════╝

ℹ Project ID: ai-build-493107
ℹ Region: us-central1
ℹ Phase: all

┌──────────────────────────────────────────────────────────────────┐
│ Deployment Plan
└──────────────────────────────────────────────────────────────────┘

ℹ Phases to execute:
  PHASE 1 - Enable Google Cloud APIs
  PHASE 2 - Setup Database & Storage
  PHASE 3 - Deploy Agents
  PHASE 4 - Deploy Main Application

⚠ This will deploy to Google Cloud Platform
Continue with deployment? (yes/no): yes

# [Phases execute automatically]

┌──────────────────────────────────────────────────────────────────┐
│ DEPLOYMENT COMPLETE ✓
└──────────────────────────────────────────────────────────────────┘

ℹ 🎉 All phases executed successfully!

ℹ 📊 Next Steps:
  1. Access your application in Cloud Console
     https://console.cloud.google.com/run?project=ai-build-493107

  2. View application logs
     gcloud logging read --limit 100 --project=ai-build-493107

✓ Deployment Ready!

# 5. Get your application URL
$ gcloud run services describe justice-ai-app --region=us-central1 --format="value(status.url)"
https://justice-ai-app-xxxxx.run.app

# 6. Test health endpoint
$ curl https://justice-ai-app-xxxxx.run.app/health
{"status": "ok"}
```

---

## 🎯 Timeline in Cloud Shell

```
Time:       Phase:                          Status:
──────────  ─────────────────────────────   ─────────────────
00:00-03:00 Phase 1: Enable APIs            ▓▓▓░░░░░░░ 30%
03:00-08:00 Phase 2: Setup Database         ▓▓▓▓▓░░░░░ 50%
08:00-28:00 Phase 3: Deploy Agents          ▓▓▓▓▓▓▓░░░ 70%
28:00-38:00 Phase 4: Deploy App             ▓▓▓▓▓▓▓▓▓░ 90%
38:00+      ✓ Complete                      ▓▓▓▓▓▓▓▓▓▓ 100%

Total Time: 30-45 minutes
```

---

## 📝 Monitoring Deployment in Cloud Shell

### Real-Time Logs

```bash
# Watch logs as deployment happens
gcloud logging read 'resource.type=cloud_run_revision' --follow --limit=50

# Or in another Cloud Shell tab
watch gcloud run services list
```

### Check Service Status

```bash
# List all deployed services
gcloud run services list

# Get specific service details
gcloud run services describe justice-ai-app --format=json | jq '.status.url'

# Check service revisions
gcloud run revisions list
```

### View Recent Logs

```bash
# Last 10 errors
gcloud logging read 'severity=ERROR' --limit=10

# Last 50 info logs
gcloud logging read 'severity>=INFO' --limit=50

# Filter by service
gcloud logging read 'resource.labels.service_name=chief-justice' --limit=20
```

---

## 🐛 Troubleshooting in Cloud Shell

### Issue: "Permission denied" on scripts

```bash
# Make scripts executable
chmod +x deploy-*.sh
./deploy-master.sh --project-id "your-project-id"
```

### Issue: "gcloud: command not found"

```bash
# Already installed, but update if needed
gcloud components update
which gcloud
```

### Issue: Docker build fails

```bash
# Cloud Shell has Docker, but ensure daemon is running
docker ps

# If not running, restart
sudo service docker restart
```

### Issue: "No such file or directory" scripts

```bash
# Verify you're in correct directory
pwd
ls -la deploy-*.sh

# Check path
cd path/to/justice-ai-workflow
./deploy-master.sh --project-id "your-project-id"
```

### Issue: Deployment timeout

```bash
# Cloud Run deployments can take 5+ minutes
# Check status in another terminal
gcloud run services describe justice-ai-app --format="value(status.currentServingRevisions)"

# View deployment events
gcloud logging read 'resource.type=cloud_run_revision' --limit=50
```

---

## 💾 Saving Script Output

Capture deployment output to a file:

```bash
# Run with output saved to file
./deploy-master.sh --project-id "your-project-id" --verbose | tee deployment-$(date +%Y%m%d-%H%M%S).log

# View the log
cat deployment-20260412-143000.log
```

---

## 🔐 Security Notes

These bash scripts:
- ✅ Use service accounts (not personal credentials)
- ✅ Only enable required APIs
- ✅ Create resources with minimal permissions
- ✅ No hardcoded credentials
- ✅ Authenticate via `gcloud auth`

**To cleanup after testing:**

```bash
# Delete all deployed services
gcloud run services delete justice-ai-app chief-justice quantitative-auditor \
    legal-researcher mitigator-juror strict-auditor-juror ethicist-juror \
    --region=us-central1 --quiet

# Disable APIs (optional)
gcloud services disable aiplatform.googleapis.com run.googleapis.com \
    firestore.googleapis.com storage-api.googleapis.com
```

---

## 🎯 Next Steps After Deployment

### 1. Access Your App

```bash
# Get the URL
gcloud run services describe justice-ai-app --format="value(status.url)"

# Open in browser (copy-paste the URL)
# Then visit: https://justice-ai-app-xxxxx.run.app
```

### 2. Test the Application

```bash
# Health check
curl https://justice-ai-app-xxxxx.run.app/health

# API docs (Swagger)
# https://justice-ai-app-xxxxx.run.app/docs
```

### 3. Monitor and Scale

```bash
# View metrics
gcloud monitoring dashboards list

# Scale a service
gcloud run deploy chief-justice --memory=2Gi --cpu=2

# Set auto-scaling
gcloud run deploy justice-ai-app --max-instances=10
```

### 4. Setup Alerts

```bash
# Create alert policy
gcloud alpha monitoring policies create --notification-channels=CHANNEL_ID \
    --display-name="Justice AI Alerts"
```

---

## 📊 Comparison: PowerShell vs Bash

| Task | PowerShell | Bash (Cloud Shell) |
|------|-----------|-------------------|
| Run all phases | `.\deploy-master.ps1` | `./deploy-master.sh` |
| Prerequisites | Docker Desktop + PowerShell 7 | Just Cloud Shell |
| Docker builds | Local machine | Cloud Shell (already has Docker) |
| Speed | Depends on local machine | Cloud-fast (good network) |
| Log persistence | Local file | Cloud Logging (built-in) |
| Cost | Free (runs locally) | Minimal (Cloud Run costs only) |

---

## ✨ Why Use Cloud Shell?

✅ **No setup needed** - Everything pre-installed  
✅ **Automatic auth** - Already connected to your project  
✅ **Fast network** - Direct to Google Cloud  
✅ **Persistent logs** - Cloud Logging stores everything  
✅ **No local resources** - Runs in the cloud  
✅ **Free tier included** - Up to 50 hours/month free  

---

## 🎓 Learning Resources

### In Cloud Shell

```bash
# View script source
cat deploy-master.sh

# See what a command does
gcloud run deploy --help

# Check current deployments
gcloud run services list --format=table

# Read recent logs
gcloud logging read --limit=100 | less
```

### Cloud Shell Tips

```bash
# Use Ctrl+C to stop long output
# Use arrow keys to scroll through command history
# Type ! to see history: !gcloud (re-run last gcloud command)
# Use tab for auto-completion
```

---

## 🚀 Ready to Deploy?

### Quick Command for Your Project

```bash
# Copy and update with your project ID, then paste into Cloud Shell:

./deploy-master.sh --project-id "ai-build-493107" --skip-confirmation
```

That's it! Your complete AI agent system will be live in 30-45 minutes.

---

**Questions?** Check the troubleshooting section above or review [STEP_BY_STEP_DEPLOYMENT.md](STEP_BY_STEP_DEPLOYMENT.md) for PowerShell version details.

**Happy Cloud Deploying!** ☁️🚀

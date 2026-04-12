# 🚀 Justice AI Workflow - Deployment Guide

This guide provides a comprehensive walkthrough for deploying the **Justice AI Workflow** both locally for development and to **Google Cloud Platform (GCP)** for production.

---

## 📋 Table of Contents

1. [Local Development](#-local-development)
2. [Google Cloud Platform Deployment](#-google-cloud-platform-deployment)
   - [Phase 1: API Enablement](#phase-1-api-enablement)
   - [Phase 2: Database & Storage Setup](#phase-2-database--storage-setup)
   - [Phase 3: Agent Deployment](#phase-3-agent-deployment)
   - [Phase 4: Main Application Deployment](#phase-4-main-application-deployment)
3. [Post-Deployment Verification](#-post-deployment-verification)
4. [Monitoring & Cost Management](#-monitoring--cost-management)

---

## 💻 Local Development

For rapid iteration and testing, you can run the entire multi-agent system locally using Docker Compose.

### Prerequisites
- Docker & Docker Desktop
- Python 3.10+
- A `.env` file (copy from `.env.example`)

### Steps
1. **Initialize the environment**:
   ```bash
   chmod +x init.sh
   ./init.sh
   ```
2. **Launch the system**:
   ```bash
   docker-compose up --build
   ```
3. **Access the Application**:
   - Frontend: `http://localhost:8080`
   - API Docs: `http://localhost:8080/docs`

---

## ☁️ Google Cloud Platform Deployment

The Justice AI Workflow is designed to run on **Cloud Run** with **Vertex AI** orchestration.

### Prerequisites
- Google Cloud SDK (`gcloud` CLI)
- An active GCP Project with billing enabled
- Docker Desktop (for building images locally)

---

### Phase 1: API Enablement

Enable the required Google Cloud services. Run this command in your terminal:

```bash
gcloud services enable \
    aiplatform.googleapis.com \
    run.googleapis.com \
    storage-api.googleapis.com \
    firestore.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    container.googleapis.com \
    compute.googleapis.com \
    servicenetworking.googleapis.com \
    cloudresourcemanager.googleapis.com
```

Alternatively, use the provided script:
```powershell
.\deploy-01-enable-apis.ps1 -ProjectID "your-project-id"
```

---

### Phase 2: Database & Storage Setup

This phase initializes **Firestore** in Native mode and creates 3 **Cloud Storage** buckets for cases, reports, and legal documents.

**Command**:
```powershell
.\deploy-02-setup-database.ps1 -ProjectID "your-project-id" -Region "us-central1"
```

---

### Phase 3: Agent Deployment

Builds and deploys the 6 specialized AI agents to Cloud Run:
1. **Chief Justice** (Orchestrator)
2. **Quantitative Auditor** (Bias Analysis)
3. **Legal Researcher** (RAG Specialist)
4. **Mitigator Juror** (Defense)
5. **Strict Auditor Juror** (Prosecution)
6. **Ethicist Juror** (Ethics)

**Command**:
```powershell
.\deploy-03-deploy-agents.ps1 -ProjectID "your-project-id" -Region "us-central1"
```

---

### Phase 4: Main Application Deployment

Deploys the central FastAPI application that ties everything together.

**Command**:
```powershell
.\deploy-04-deploy-app.ps1 -ProjectID "your-project-id" -Region "us-central1"
```

> [!TIP]
> You can run all phases automatically using the master script:
> ```powershell
> .\deploy-master.ps1 -ProjectID "your-project-id" -SkipConfirmation
> ```

---

## ✅ Post-Deployment Verification

After deployment, verify the system is running correctly:

1. **Check Service Status**:
   ```bash
   gcloud run services list
   ```
2. **Health Check**:
   Navigate to `https://[your-app-url]/health` - it should return `{"status": "healthy"}`.
3. **Test Workflow**:
   Submit a test case through the UI and monitor the logs to see agents interacting.

---

## 📊 Monitoring & Cost Management

- **Logs**: View real-time logs in the [Google Cloud Console](https://console.cloud.google.com/logs).
- **Cost Estimation**:
  - **Cloud Run**: ~$40-60/month (depending on traffic)
  - **Vertex AI**: ~$50-100/month (based on tokens)
  - **Total**: Approx. $150-250/month for production.

> [!CAUTION]
> Always set **auto-scaling limits** on Cloud Run to prevent unexpected billing spikes during high load.

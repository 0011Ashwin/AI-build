# Justice AI Workflow - CI/CD Pipeline Setup Guide

This guide explains how to set up continuous integration and deployment (CI/CD) for the Justice AI Workflow system using Google Cloud Build.

## Overview

The CI/CD pipeline automates:
- Building Docker images on every code commit
- Running tests
- Pushing images to Artifact Registry
- Deploying services to Cloud Run
- Running post-deployment verification

## Architecture

```
Git Repository (GitHub/Cloud Source Repositories)
         ↓
   Commit Trigger
         ↓
   Cloud Build (cloudbuild.yaml)
         ↓
   Build 7 Docker Images
         ↓
   Push to Artifact Registry
         ↓
   Deploy to Cloud Run
         ↓
   Run Tests & Verification
         ↓
   ✅ Deployment Complete
```

## Configuration Files

### 1. cloudbuild.yaml

**Location**: `d:\Gen-test-02\justice-ai-workflow\cloudbuild.yaml`

This file defines the complete build pipeline:
- Builds all 7 Docker images
- Pushes images to Artifact Registry
- Deploys services to Cloud Run
- Runs health checks

### 2. deploy-to-cloud.ps1

**Location**: `d:\Gen-test-02\justice-ai-workflow\deploy-to-cloud.ps1`

PowerShell script for local or automated deployment:
- Validates prerequisites
- Creates GCP resources
- Builds and pushes images
- Deploys to Cloud Run
- Verifies deployment

## Setup Instructions

### Step 1: Connect Your Repository

```bash
# If using GitHub
gcloud builds connect github

# If using Cloud Source Repositories
gcloud source repos create justice-ai-workflow
```

### Step 2: Create Build Trigger

```powershell
# Create trigger via gcloud
gcloud builds triggers create github `
    --name="justice-ai-deploy" `
    --repo-name="<YOUR_GITHUB_REPO>" `
    --repo-owner="<YOUR_GITHUB_USERNAME>" `
    --branch-pattern="^main$" `
    --build-config="cloudbuild.yaml" `
    --service-account="projects/$PROJECT_ID/serviceAccounts/justice-ai-sa@$PROJECT_ID.iam.gserviceaccount.com"
```

Or via Google Cloud Console:
1. Go to Cloud Build > Triggers
2. Click "Create Trigger"
3. Select your repository
4. Configure:
   - Name: `justice-ai-deploy`
   - Branch: `^main$`
   - Build configuration: `cloudbuild.yaml`

### Step 3: Grant Cloud Build Service Account Permissions

```powershell
# Get Cloud Build service account
$CLOUD_BUILD_SA = "<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com"

# Assign roles
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --role="roles/editor"  # Use more restrictive role in production
```

### Step 4: Push to Repository

```bash
cd d:\Gen-test-02\justice-ai-workflow

git init
git add .
git commit -m "Initial Justice AI Workflow deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Monitoring Builds

### View Build Logs

```powershell
# List recent builds
gcloud builds list --limit=10

# View specific build logs
gcloud builds log <BUILD_ID>

# Stream build logs in real-time
gcloud builds log <BUILD_ID> --stream

# List builds for trigger
gcloud builds list --filter="substitutions._TRIGGER_NAME=justice-ai-deploy"
```

### Check Build Status

```powershell
# View all build run history
gcloud builds list --format="table(ID,STATUS,SUBSTITUTIONS._TRIGGER_NAME,CREATE_TIME)"

# Get build details
gcloud builds describe <BUILD_ID>

# View build steps
gcloud builds describe <BUILD_ID> --format="table(steps[].name,steps[].status)"
```

## Advanced Configuration

### Environment Variables in Builds

Modify `cloudbuild.yaml` substitutions variable section:

```yaml
substitutions:
  _REGISTRY: '${_REGION}-docker.pkg.dev/${PROJECT_ID}/justice-ai-repository'
  _REGION: 'us-central1'
  _SERVICE_ACCOUNT: 'justice-ai-sa@${PROJECT_ID}.iam.gserviceaccount.com'
  _ARTIFACT_REGISTRY: 'justice-ai-repository'
```

### Conditional Deployments

Only deploy on tags:

```yaml
# In cloudbuild.yaml
options:
  machineType: 'N1_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
  onFailure:
    - NOTIFY
```

### Custom Build Steps

Add custom steps to `cloudbuild.yaml`:

```yaml
steps:
  # ... existing steps ...
  
  # Run tests
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'run'
      - '${_REGISTRY}/justice-ai-app:${SHORT_SHA}'
      - 'pytest'
      - '/app/tests'
    env:
      - 'GOOGLE_PROJECT_ID=${PROJECT_ID}'
  
  # Security scan
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - 'run'
      - '--filename=./'
      - '--image=${_REGISTRY}/justice-ai-app:${SHORT_SHA}'
      - '--location=us-central1'
```

## Rollback Procedures

### Rollback to Previous Deployment

```powershell
# Get previous revision
gcloud run services describe justice-ai-app `
    --region=us-central1 `
    --format="value(status.traffic[1].revision.name)"

# Switch traffic to previous revision
gcloud run services update-traffic justice-ai-app `
    --region=us-central1 `
    --to-revisions LATEST=0,<PREVIOUS_REVISION>=100

# Or redeploy previous image
gcloud run deploy justice-ai-app `
    --image="${_REGISTRY}/justice-ai-app:<PREVIOUS_TAG>" `
    --region=us-central1
```

## Deployment Failures

### Common Build Failures

**1. Docker Build Fails**
```powershell
# Check Dockerfile
docker build -f agents/chief_justice/Dockerfile agents/chief_justice --no-cache

# View detailed build output
gcloud builds log <BUILD_ID> --stream
```

**2. Artifact Registry Push Fails**
```powershell
# Verify service account has storage.admin role
gcloud projects get-iam-policy $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --format="table(role)"

# Re-grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --role="roles/artifactregistry.writer"
```

**3. Cloud Run Deployment Fails**
```powershell
# Check Cloud Run API is enabled
gcloud services list --enabled | grep run.googleapis.com

# Check service account has run.admin role
gcloud projects get-iam-policy $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --filter="bindings.role:roles/run.admin"
```

## Manual Build Trigger

If you need to manually trigger a build:

```powershell
# Trigger build manually
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_TRIGGER_NAME="manual-build,_REGION=us-central1"

# Submit specific branch
gcloud builds submit \
    --branch=main \
    --config=cloudbuild.yaml
```

## Build Notifications

### Slack Integration

1. **Create Slack Incoming Webhook**:
   - Go to: https://api.slack.com/messaging/webhooks
   - Create new app → Incoming Webhooks
   - Copy webhook URL

2. **Store in Secret Manager**:
```powershell
gcloud secrets create slack-webhook-url \
    --replication-policy="automatic" \
    --data-file=- <<< "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

3. **Add Notification Step to cloudbuild.yaml**:
```yaml
onFailure:
  - name: 'gcr.io/cloud-builders/gke-deploy'
    env:
      - 'SLACK_WEBHOOK=$(cat /workspace/slack-url)'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        curl -X POST $SLACK_WEBHOOK \
        -H 'Content-Type: application/json' \
        -d '{
          "text": "Build '"$BUILD_ID"' failed",
          "attachments": [{
            "color": "danger",
            "text": "Justice AI deployment failed"
          }]
        }'
```

## Best Practices

### 1. Version Tagging

Tag images with semantic versioning:

```yaml
images:
  - '${_REGISTRY}/justice-ai-app:latest'
  - '${_REGISTRY}/justice-ai-app:${SHORT_SHA}'
  - '${_REGISTRY}/justice-ai-app:v1.0.0'  # Add version tag
```

### 2. Build Caching

```yaml
options:
  machineType: 'N1_HIGHCPU_8'
  # Use cache for faster builds
  substitutionOption: 'ALLOW_LOOSE'
```

### 3. Secure Secrets

```yaml
steps:
  - name: 'gcr.io/cloud-builders/gke-deploy'
    secretEnv:
      - 'DB_PASSWORD'
      - 'API_KEY'
    env:
      - 'DB_USER=admin'

availableSecrets:
  secretManager:
    - versionName: projects/$PROJECT_ID/secrets/db-password/versions/latest
      env: 'DB_PASSWORD'
    - versionName: projects/$PROJECT_ID/secrets/api-key/versions/latest
      env: 'API_KEY'
```

### 4. Build Timeout

Set appropriate timeout:

```yaml
timeout: '3600s'  # 1 hour
```

## Cost Optimization

### Build Quotas

```powershell
# View build usage
gcloud builds list --filter="createTime>=$(date -u -d 'today' +%Y-%m-%dT%H:%M:%S)Z"

# Set budget alert
gcloud billing budgets create \
    --billing-account=$BILLING_ACCOUNT \
    --display-name="Cloud Build Budget" \
    --budget-amount=100 \
    --threshold-rule=percent=50 \
    --threshold-rule=percent=90
```

### Optimize Machine Type

```yaml
options:
  # Use smaller machine for faster builds
  machineType: 'N1_HIGHCPU_8'  # 8 vCPU, ~20-30 min builds
  # Or
  machineType: 'N1_HIGHCPU_32'  # 32 vCPU, ~5-10 min builds
```

## Deployment Statistics

### Build Metrics

```powershell
# Average build time
gcloud builds list --limit=100 --format="table(startTime,finishTime)" | \
  awk '{print ($2 - $1)}' | 'awk '{sum+=$1; count++} END {print sum/count}'

# Success rate
gcloud builds list --limit=100 --format="table(status)" | \
  grep -c "SUCCESS" / 100 * 100

# Build frequency
gcloud builds list --limit=100 --format="table(id,createTime)"
```

## Complete Deployment Workflow

### Development → Production

```
1. Developer commits code to main branch
                    ↓
2. GitHub webhook triggers Cloud Build
                    ↓
3. Cloud Build executes cloudbuild.yaml:
   a. Builds 7 Docker images
   b. Runs security scan
   c. Pushes to Artifact Registry
   d. Deploys to Cloud Run
   e. Runs integration tests
                    ↓
4. Deployment successful ✅
                    ↓
5. Slack notification sent
                    ↓
6. Application live and running
```

## Troubleshooting Cloud Build

### Build Step Failures

```powershell
# View failed step details
gcloud builds describe <BUILD_ID> --format="json" | jq '.failureMessage'

# View all step logs
gcloud builds log <BUILD_ID> --stream

# Retry failed build
gcloud builds retry <BUILD_ID>
```

### Service Account Issues

```powershell
# List service accounts
gcloud iam service-accounts list

# Check Cloud Build service account
$CLOUD_BUILD_SA = "$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com"

# View permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:$CLOUD_BUILD_SA"
```

## Summary

Your CI/CD pipeline is now:

✅ **Automated**: Builds trigger on every code push
✅ **Scalable**: Handles all 7 services in parallel
✅ **Reliable**: Includes rollback procedures
✅ **Observable**: Logs and notifications enabled
✅ **Secure**: Uses Secret Manager for credentials
✅ **Cost-effective**: Configurable build resources

---

**Files to commit to repository:**
- `cloudbuild.yaml`
- `deploy-to-cloud.ps1`
- `DEPLOYMENT_AUTOMATION_GUIDE.md`
- `CI_CD_SETUP_GUIDE.md` (this file)

---

*Last Updated: 2024*
*Project: Justice AI Workflow CI/CD on Google Cloud Platform*

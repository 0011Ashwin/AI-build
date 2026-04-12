# Troubleshooting IAM Role Assignment Errors
## Justice AI Workflow Deployment Issues

---

## 🚨 Error: "Failed to assign IAM role"

When you see this error:
```
✗ ERROR: Phase execution failed
```

During Phase 3 (Deploy Agents) at IAM role assignment, it means your account **doesn't have permission to assign IAM roles**.

---

## 🔍 Root Cause

The deployment script is trying to run:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="roles/aiplatform.user"
```

This requires your user account to have one of these roles:
- `roles/iam.securityAdmin` (Can manage IAM)
- `roles/iam.admin` (Can administer IAM)
- `roles/editor` (Project Editor)
- `roles/owner` (Project Owner)

If you don't have these, the command will fail.

---

## ✅ Solution: Two Options

### **Option 1: Ask Project Owner/Admin**

If you're **not** the project owner, ask them to:

1. Go to: https://console.cloud.google.com/iam-admin/iam
2. Click **Grant Access**
3. Add your email
4. Assign role: **Project Editor** or **IAM Security Admin**
5. Click Save

Then try deployment again.

---

### **Option 2: You're the Owner - Fix Your Role**

If you **are** the project owner but still getting the error:

#### Step 1: Check Your Current Role

```bash
gcloud projects get-iam-policy ai-build-493107 --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:user@your-email.com"
```

#### Step 2: Ensure You Have Editor Role

```bash
# Go to Cloud Console
# https://console.cloud.google.com/iam-admin/iam?project=ai-build-493107

# Look for your email in the list
# Verify you have "Editor" or "Owner" role
# If not, click Edit → Add role → Editor
```

#### Step 3: Retry Deployment

```bash
./deploy-master.sh --project-id "ai-build-493107"
```

---

## 🛠️ Workaround: Skip IAM Assignment

If you can't get the required permissions, use this workaround:

### Step 1: Edit the Deployment Script

```bash
nano deploy-03-deploy-agents.sh
```

### Step 2: Comment Out IAM Role Assignment

Find this section (around line 164):
```bash
# Assign roles
write_info "Assigning required IAM roles..."
ROLES=(...)

for role in "${ROLES[@]}"; do
    ...
done
```

Comment it out:
```bash
# Assign roles
# write_info "Assigning required IAM roles..."
# ROLES=(...)
# 
# for role in "${ROLES[@]}"; do
#     ...
# done

write_success "Service account roles pre-configured (skipped)"
```

### Step 3: Run Deployment

The agents will deploy without explicit role assignment (they'll use default service account permissions).

---

## 🔑 Check Your Current Permissions

Run these commands to see what roles you have:

```bash
# Get your email
gcloud config get-value account

# Check your roles on the project
gcloud projects get-iam-policy ai-build-493107 \
    --flatten="bindings[].members" \
    --filter="bindings.members:$(gcloud config get-value account)" \
    --format="table(bindings.role)"

# Or simpler - list all IAM members
gcloud projects get-iam-policy ai-build-493107 \
    --format="table(bindings.role,bindings.members)"
```

---

## 📋 Who Can Assign IAM Roles?

Only these roles can assign IAM roles to others:

| Role | Can Assign IAM? | Notes |
|------|-----------------|-------|
| **Owner** | ✅ Yes | Has all permissions |
| **Editor** | ✅ Yes | Can manage most things |
| **Security Admin** | ✅ Yes | Can manage IAM only |
| **Viewer** | ❌ No | Read-only access |
| **User** | ❌ No | Limited permissions |
| **Service Account** | ❌ No | Cannot assign roles to itself |

---

## 🚀 Quick Fix Steps

### If You're the Project Owner:

1. Open: https://console.cloud.google.com/iam-admin/iam
2. Find your email in the list
3. Verify you have **Editor** or **Owner** role
4. If not → **Edit** → **Add Role** → **Editor**
5. **Save**
6. Retry deployment

### If You're Not the Owner:

1. Ask project owner for: **Editor** or **Security Admin** role
2. Provide them your email: `gcloud config get-value account`
3. They go to: https://console.cloud.google.com/iam-admin/iam
4. Click **Grant Access**
5. Add your email, assign **Editor** role
6. You retry deployment

---

## 🔧 Alternative: Deploy with Manual IAM Assignment

If permissions are limited, assign roles manually:

```bash
# Your project owner runs these commands:
PROJECT_ID="ai-build-493107"
SERVICE_ACCOUNT_EMAIL="justice-ai-sa@ai-build-493107.iam.gserviceaccount.com"

# Assign roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/firestore.viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/logging.logWriter"

echo "Roles assigned successfully!"
```

Then you can run the deployment again without IAM assignment.

---

## ⚠️ Important: Service Account vs User Permissions

The error message is misleading - it's **YOUR permissions**, not the service account's!

- **Service Account**: `justice-ai-sa` (needs Vertex AI, Storage, Firestore access)
- **Your User Account**: (needs IAM security admin to assign roles to service account)

You need **both** to work.

---

## ✅ Verify Success

After fixing permissions, you should see:

```bash
# Run this to verify roles are assigned
gcloud projects get-iam-policy ai-build-493107 \
    --flatten="bindings[].members" \
    --filter="bindings.members:justice-ai-sa@*" \
    --format="table(bindings.role)"

# Output should show:
# ROLE
# roles/aiplatform.user
# roles/storage.objectViewer
# roles/firestore.viewer
# roles/logging.logWriter
```

---

## 📞 Still Not Working?

Try these commands for debugging:

```bash
# 1. Verify you're authenticated as the right account
gcloud auth list

# 2. Check your email and current project
gcloud config list

# 3. Try manual role assignment to see actual error
gcloud projects add-iam-policy-binding ai-build-493107 \
    --member="serviceAccount:justice-ai-sa@ai-build-493107.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
# Look at the actual error message

# 4. Check if service account exists
gcloud iam service-accounts list --project=ai-build-493107

# 5. Review project policy
gcloud projects get-iam-policy ai-build-493107 | grep -A5 "your-email@"
```

---

## 🎯 Summary

| Error | Cause | Fix |
|-------|-------|-----|
| "Failed to assign IAM" | You don't have IAM Security Admin role | Ask owner for Editor role |
| "Permission denied" | Account has Viewer role only | Get upgraded to Editor |
| "Binding already exists" | Role already assigned | This is OK, continue |
| "Service account not found" | Wrong email format | Check service account EMAIL |

---

## 🔐 Security Best Practice

For production deployments:

1. **Only grant roles you need** - Don't give Owner to everyone
2. **Use Service Accounts** - Don't use personal accounts for deployment
3. **Rotate credentials** - Change service account keys regularly
4. **Enable audit logs** - Track who makes what changes
5. **Test with minimal roles** - Verify least privilege works

---

**Need more help?** Check these resources:

- [Google Cloud IAM Roles](https://cloud.google.com/iam/docs/understanding-roles)
- [Grant IAM Roles on Projects](https://cloud.google.com/iam/docs/granting-changing-revoking-access)
- [Service Account Permissions](https://cloud.google.com/iam/docs/service-account-permissions)

---

## ✅ After Fixing Permissions

Once you have the right role (Editor or Security Admin):

```bash
# Re-run Phase 3 deployment
./deploy-03-deploy-agents.sh --project-id "ai-build-493107"

# Or the full deployment
./deploy-master.sh --project-id "ai-build-493107"
```

Should work now! 🎉

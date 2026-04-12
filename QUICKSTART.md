# Quick Reference Guide

## 🚀 Get Started in 3 Steps

### Step 1: Initialize Project
```bash
cd justice-ai-workflow
bash init.sh
```

### Step 2: Start Local Development
```bash
bash run_local.sh
```

### Step 3: Open Web UI
Navigate to `http://localhost:8000` in your browser

---

## 📋 Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI server & workflow orchestrator |
| `agents/*/agent.py` | Individual agent logic |
| `shared/bias_calculator.py` | Bias metrics calculations |
| `shared/vector_search_client.py` | Legal precedent retrieval |
| `app/frontend/index.html` | Web user interface |

---

## 🔧 Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Docker Compose
docker-compose up

# Start individual agent
python agents/chief_justice/adk_app.py

# Run main server
python app/main.py

# Deploy to Google Cloud
bash deploy.sh your-project-id us-central1
```

---

## 📊 Testing the System

### Submit a test case via API:
```bash
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{
    "case_data": {
      "case_id": "test_001",
      "name": "Jane Smith",
      "age": 28,
      "priors": 1,
      "zip_code": "10001",
      "original_score": 68.5,
      "decision_type": "lending",
      "jurisdiction": "US Federal"
    }
  }'
```

### Check audit status:
```bash
curl http://localhost:8000/status/test_001
```

### Get audit report:
```bash
curl http://localhost:8000/reports/test_001
```

---

## 🏗️ System Architecture

```
Frontend (React) ──► FastAPI Server
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Chief Justice    Jury Panel     Specialists
     (Orchestrator)   (3 Agents)     (3 Agents)
        │                │                │
        └────────────────┼────────────────┘
                         │
          Google Cloud Platform
          (Vertex AI, Vector Search)
```

---

## 📈 Bias Score Interpretation

| Score | Risk Level | Interpretation |
|-------|-----------|---|
| 0-30 | LOW | Algorithm appears fair |
| 30-50 | MEDIUM | Some concerns, monitor |
| 50-70 | HIGH | Significant bias detected |
| 70-100 | CRITICAL | Likely discriminatory |

---

## ⚖️ Jury Verdict Guide

- **FAIR**: Algorithm passes fairness standards
- **FAIR_WITH_CONCERNS**: Accept with monitoring
- **UNFAIR**: Reject or substantially revise

Verdicts determined by majority vote among 3 Jurors

---

## 🌐 Agents Overview

| Agent | Port | Function |
|-------|------|----------|
| Chief Justice | 8001 | Orchestrator |
| Quantitative Auditor | 8002 | Bias calculations |
| Legal Researcher | 8003 | Legal precedents |
| Mitigator Juror | 8004 | Defense view |
| Strict Auditor Juror | 8005 | Prosecutor view |
| Ethicist Juror | 8006 | Ethics view |

---

## 📚 Read More

- Full guide: See `README.md`
- Architecture: See `ARCHITECTURE.md`
- Project details: See `PROJECT_SUMMARY.md`

---

## 🆘 Troubleshooting

### Port already in use?
```bash
# Change port in app/main.py or use docker-compose with different mapping
```

### Google Cloud authentication error?
```bash
gcloud auth application-default login
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/application_default_credentials.json
```

### Agent not responding?
```bash
# Check if agent container is running
docker ps | grep agent

# View agent logs
docker logs <agent_container_id>
```

---

**Ready to audit for fairness? Start here! 🚀**

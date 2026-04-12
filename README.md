# ⚖️ Justice AI Workflow

### *Fairness-First Algorithmic Auditing System*

A sophisticated multi-agent AI system built to audit algorithmic fairness and detect bias in automated decision-making. Powered by **Gemini Pro** and **Google Cloud Vertex AI**.

---

## 🏛️ System Architecture

The Justice AI Workflow employs a **Multi-Agent Jury** approach to evaluate bias from multiple ethical and legal perspectives.

### 🎭 The 6-Agent Jury
- **Chief Justice**: The central orchestrator managing the auditing workflow.
- **Quantitative Auditor**: Expert in statistical bias and Disparate Impact calculations.
- **Legal Researcher**: Specialist in legal precedents (powered by Contextual RAG).
- **Mitigator Juror**: The Defense advocate looking for contextual fairness factors.
- **Strict Auditor Juror**: The Prosecution advocate flagging potential proxy biases.
- **Ethicist Juror**: Focuses on human impact and SDG alignment.

---

## 🚀 Getting Started

To get the system up and running, please refer to our comprehensive guide:

### 👉 [**DEPLOYMENT_GUIDE.md**](./DEPLOYMENT_GUIDE.md)

This guide covers:
- 🏗️ **Local Development**: Run the entire system with Docker Compose.
- ☁️ **GCP Deployment**: Step-by-step instructions for Cloud Run & Vertex AI.
- 🔑 **API Setup**: Commands to enable required Google Cloud Services.

---

## 📊 Key Features

- **Automated Bias Detection**: Calculates Disparate Impact Ratios and Statistical Parity.
- **Contextual RAG**: Retrieves relevant legal precedents and case law.
- **Collaborative Decision Making**: Agents debate cases to reach a final verdict.
- **Dynamic Reporting**: Generates comprehensive audit reports for review.

---

## 📁 Project Structure

```text
justice-ai-workflow/
├── agents/             # Specialist AI Agent microservices
├── app/               # Main FastAPI application & Web UI
├── shared/            # Shared utilities for bias calculation & RAG
├── DEPLOYMENT_GUIDE.md # 📖 COMPLETE DEPLOYMENT INSTRUCTIONS
├── docker-compose.yaml # Local orchestration
└── requirements.txt    # Python dependencies
```

---

**Built with Google Cloud ADK** | **Powered by Gemini AI** | **Committed to Fairness**

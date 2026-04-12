# Justice AI Workflow: Fairness-First Algorithmic Auditing System

A sophisticated multi-agent AI system built with ADK for auditing algorithmic fairness and detecting bias in automated decision-making systems.

## 🏗️ Architecture Overview

This system implements a **5-State Workflow** for comprehensive algorithmic fairness auditing:

### States
1. **STATE 1: Intake Node** - Collects case data (demographics, scores, proxy data)
2. **STATE 2: Audit Chamber** - Quantitative bias analysis (Disparate Impact Ratio, Counterfactual Analysis)
3. **STATE 3: Contextual RAG** - Legal precedent retrieval from Vector Database
4. **STATE 4: Jury Verdict** - Multi-agent debate with 3 distinct perspectives
5. **STATE 5: Mitigation & Reporting** - Final verdict and bias-corrected scoring

## 👥 6-Agent Hierarchy

### Root Agent
- **Chief Justice** - Orchestrator managing the entire workflow

### Specialist Agents
1. **Quantitative Auditor** - Statistical bias calculations
2. **Legal Researcher** - Legal precedent retrieval (RAG)
3. **Mitigator Juror** - Defense perspective (contextual factors)
4. **Strict Auditor Juror** - Prosecutor perspective (proxy bias flagging)
5. **Ethicist Juror** - Human impact & SDG alignment assessment

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Cloud Project with ADK enabledment
- Docker & Docker Compose (for deployment)

### Installation

```bash
# Clone the repository
cd justice-ai-workflow

# Install dependencies
pip install -r requirements.txt

# Configure Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Running Locally

```bash
# Start main application
python app/main.py

# Start individual agents (in separate terminals)
python agents/chief_justice/adk_app.py
python agents/quantitative_auditor/adk_app.py
python agents/legal_researcher/adk_app.py
python agents/mitigator_juror/adk_app.py
python agents/strict_auditor_juror/adk_app.py
python agents/ethicist_juror/adk_app.py
```

### Access Web UI
Navigate to `http://localhost:8000` in your browser

## 📊 Key Metrics & Standards

### Disparate Impact Ratio (DIR)
- **Formula**: P(Favorable | Group A) / P(Favorable | Group B)
- **Safe Harbor**: DIR ≥ 0.80 (80% Rule)
- **Red Flag**: DIR < 0.80 indicates disparate impact

### Bias Score
- **Range**: 0-100 (higher = more biased)
- **Components**:
  - Disparate Impact Score (0-40 points)
  - Counterfactual Score (0-30 points)
  - Statistical Parity Score (0-30 points)

### Risk Levels
- **LOW**: Bias Score < 30
- **MEDIUM**: Bias Score 30-50
- **HIGH**: Bias Score 50-70
- **CRITICAL**: Bias Score > 70

## 🔍 API Endpoints

### Core Audit Endpoint
```
POST /audit
Content-Type: application/json

{
    "case_data": {
        "case_id": "case_001",
        "name": "John Doe",
        "age": 35,
        "priors": 2,
        "zip_code": "12345",
        "original_score": 75.5,
        "decision_type": "hiring",
        "jurisdiction": "US Federal"
    }
}
```

### Response
```json
{
    "case_id": "case_001",
    "verdict": "FAIR_WITH_CONCERNS",
    "confidence": 0.85,
    "bias_score": 45.3,
    "report_url": "/reports/case_001"
}
```

### Get Audit Report
```
GET /reports/{case_id}
```

### Get Workflow Status
```
GET /status/{case_id}
```

### System Metrics
```
GET /metrics
```

## 🐳 Docker Deployment

### Build Images
```bash
docker-compose build
```

### Run System
```bash
docker-compose up
```

### Stop System
```bash
docker-compose down
```

## 📁 Project Structure

```
justice-ai-workflow/
├── agents/
│   ├── chief_justice/          # Main orchestrator
│   ├── quantitative_auditor/   # Bias calculations
│   ├── legal_researcher/       # Legal RAG
│   ├── mitigator_juror/        # Defense perspective
│   ├── strict_auditor_juror/   # Prosecutor perspective
│   └── ethicist_juror/         # Ethics & SDG alignment
├── app/
│   ├── main.py                 # FastAPI application
│   ├── frontend/               # Web UI
│   │   ├── index.html
│   │   ├── app.js
│   │   └── style.css
│   └── Dockerfile
├── shared/
│   ├── bias_calculator.py      # Bias calculations
│   ├── vector_search_client.py # Legal precedent retrieval
│   ├── report_generator.py     # PDF report generation
│   ├── a2a_utils.py            # Agent-to-Agent communication
│   └── authenticated_httpx.py  # Google Cloud auth
├── README.md
├── requirements.txt
├── docker-compose.yaml
└── deploy.sh
```

## 🔐 Security Considerations

- All agents run in isolated containers
- Service account authentication for Google Cloud
- End-to-end encryption for sensitive data
- Audit logging of all decisions
- Rate limiting on API endpoints

## 📚 Legal & Ethical Framework

This system is built on:
- **80% Rule** (Disparate Impact Analysis)
- **Disparate Impact Doctrine** (Griggs v. Duke Power)
- **UN Sustainable Development Goals** (SDG 10 & 16)
- **Fair Lending Standards** (Fair Housing Act, Equal Employment)
- **Algorithm Accountability Principles**

## 🚨 Audit Verdicts

### FAIR
Algorithm meets fairness standards. Proceed with consideration of ongoing monitoring.

### FAIR_WITH_CONCERNS
Algorithm has acceptable performance but should be monitored. Recommend refinement before broader deployment.

### UNFAIR
Algorithm demonstrates bias or disparate impact. Recommend substantial revision or alternative approach.

## 🤝 Contributing

To add new bias detection methods or legal precedents:

1. Create a new specialized agent
2. Implement the necessary analysis tools
3. Integrate with the Chief Justice orchestrator
4. Add test cases

## 📝 License

Proprietary - Justice AI Workflow v1.0

## 📧 Support

For issues, feature requests, or collaboration: team@justiceai.org

---

**Built with Google Cloud ADK** | **Powered by Gemini AI** | **Committed to Algorithmic Fairness**

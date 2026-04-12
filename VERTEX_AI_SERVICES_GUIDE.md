# GCP Services & APIs Reference

## Complete Vertex AI Integration Guide

### 1. Vertex AI Generative AI (Gemini) - For LLM Agents

**Used in States:** 2, 4, 5

**Agents using Gemini:**
- Quantitative Auditor (State 2) - Bias analysis prompts
- Mitigator Juror (State 4) - Defense reasoning
- Strict Auditor Juror (State 4) - Prosecution analysis
- Ethicist Juror (State 4) - Ethics evaluation

**API Endpoint:**
```
https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/gemini-1.5-pro:generateContent
```

**Models Available:**
- `gemini-1.5-pro` - High performance (juice for complex analysis)
- `gemini-1.5-flash` - Fast & cost-effective (for reporting)
- `gemini-pro-vision` - Multimodal (for document analysis)

**Authentication:**
```python
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
credentials = Credentials.from_service_account_file(
    'service-account-key.json',
    scopes=SCOPES
)
```

**Sample Usage:**
```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project='PROJECT_ID', location='us-central1')
model = GenerativeModel('gemini-1.5-pro')

response = model.generate_content(
    "Analyze this bias: DIR = 0.82..."
)
print(response.text)
```

---

### 2. Vertex AI Vector Search - For Legal Precedent Retrieval (State 3 - RAG)

**Purpose:** Semantic search over legal documents database

**API Endpoint:**
```
https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/indexes/{INDEX_ID}/search
```

**Configuration:**

```yaml
Index Configuration:
  displayName: "justice-ai-legal-precedents"
  indexConfig:
    treeAhConfig:
      leafNodeEmbeddingCount: 1000
  description: "Vector database for legal precedents"
  
  Embeddings:
    model: "text-embedding-004"
    dimensions: 768
    
  Index Update Strategy:
    type: "BATCH_UPDATES"
    updateFrequency: "DAILY"
```

**Python Implementation:**

```python
from vertexai.resources.preview import vector_search

def query_legal_precedents(query_text: str, top_k: int = 3):
    """Query vector search for legal precedents"""
    
    client = vector_search.VectorSearchServiceClient(
        api_endpoint='us-central1-aiplatform.googleapis.com:443'
    )
    
    # Generate embedding for query
    response = client.search(
        index="projects/PROJECT_ID/locations/us-central1/indexes/justice-ai-legal-precedents",
        query=vector_search.Query(
            rrf=vector_search.RRFParameters(
                deployed_index_id="justice-ai-legal-precedents",
                neighbor_count=top_k
            )
        )
    )
    
    return response.neighbors
```

---

### 3. Vertex AI Model Garden - Pre-trained Models

**Available Models:**
- Text classification
- Named entity recognition (for case analysis)
- Question answering (for legal context)
- Summarization (for case briefs)

---

### 4. Vertex AI Explainable AI (XAI)

**Purpose:** Explain bias decisions

**API Endpoint:**
```
https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/models/{MODEL_ID}:explain
```

**Use Case:** Provide feature attribution for bias scores

```python
def explain_bias_decision(features: dict) -> dict:
    """Get explanation for bias score"""
    
    explanations = model.explain(
        instances=[features],
        parameters={"top_k": 5}  # Top 5 contributing factors
    )
    
    return {
        "bias_score": explanations.predictions[0],
        "feature_attributions": explanations.explanations[0].attributions
    }
```

---

### 5. Vertex AI Batch Prediction & Workbench

**For:** Running bulk audits and pilot testing

```bash
# Create batch request
gcloud ai batch-predictions create \
    --display-name="justice-ai-batch-audit" \
    --input_config='instances_format=jsonl' \
    --input_data_uri="gs://justice-ai-case-files/batch_cases.jsonl" \
    --output_config='predictions_format=jsonl' \
    --output_data_uri="gs://justice-ai-reports/batch_results/" \
    --model="projects/PROJECT_ID/locations/us-central1/models/MODEL_ID"
```

---

## Complete API Reference

### Vertex AI Endpoints (us-central1)

| Service | Endpoint | Port |
|---------|----------|------|
| Generative AI | `us-central1-aiplatform.googleapis.com` | 443 |
| Vector Search | `us-central1-aiplatform.googleapis.com` | 443 |
| Model Serving | `us-central1-aiplatform.googleapis.com` | 443 |
| Embeddings API | `us-central1-aiplatform.googleapis.com` | 443 |
| Tensorboard | `us-central1-aiplatform.googleapis.com` | 443 |

### Authentication Headers

All Vertex AI requests require:

```python
{
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

### Rate Limits

| API | Requests per Minute | Requests per Day |
|-----|-------------------|------------------|
| Gemini | 300 | 10,000,000 |
| Vector Search | 100 | 1,000,000 |
| Embeddings | 300 | 10,000,000 |

---

## Implementation Examples

### Example 1: Using Gemini for Jury Debate

```python
import vertexai
from vertexai.generative_models import GenerativeModel, GenerativeConfig

vertexai.init(project="PROJECT_ID", location="us-central1")

def jury_debate(case_data: dict, audit_findings: dict) -> dict:
    """Run 3-agent jury debate using Gemini"""
    
    model = GenerativeModel("gemini-1.5-pro")
    
    # Mitigator Juror Prompt
    mitigator_prompt = f"""
    You are the Mitigator Juror (Defense advocate).
    
    Case: {case_data}
    Audit Findings: {audit_findings}
    
    Find contextual justifications for the bias detected.
    Provide your verdict: FAIR / FAIR_WITH_CONCERNS / UNFAIR
    """
    
    mitigator_response = model.generate_content(
        mitigator_prompt,
        generation_config=GenerativeConfig(
            max_output_tokens=500,
            temperature=0.7
        )
    )
    
    return {
        "mitigator_verdict": mitigator_response.text
    }
```

### Example 2: Vector Search for Legal Precedents

```python
from google.cloud import aiplatform

def search_legal_precedents(bias_type: str, top_k: int = 5):
    """Search Vector Database for legal precedents"""
    
    client = aiplatform.MatchingEngineServiceClient(
        client_options=aiplatform.ClientOptions(
            api_endpoint="us-central1-aiplatform.googleapis.com"
        )
    )
    
    deployed_index = (
        f"projects/{PROJECT_ID}/locations/us-central1/"
        f"indexes/justice-ai-legal-precedents/"
        f"deployedIndexes/justice-ai-legal-precedents"
    )
    
    query_embedding = embeddings.embed(bias_type)
    
    response = client.find_neighbors(
        deployed_index_id=deployed_index,
        queries=[query_embedding],
        neighbor_count=top_k
    )
    
    return response.nearest_neighbors
```

### Example 3: Batch Prediction for Audits

```python
from google.cloud import aiplatform
import json

def run_batch_audit(case_file_uri: str):
    """Run batch prediction for multiple cases"""
    
    batch_prediction = aiplatform.BatchPredictionJob.create(
        display_name="justice-ai-batch-audit",
        model_name=f"projects/{PROJECT_ID}/locations/us-central1/models/{MODEL_ID}",
        instances_format="jsonl",
        predictions_format="jsonl",
        input_data_uri=case_file_uri,
        output_data_uri=f"gs://justice-ai-reports/batch_{datetime.now().date()}/",
        machine_type="n1-standard-4",
        sync=False
    )
    
    return batch_prediction
```

---

## Monitoring & Observability with Vertex AI

### Model Monitoring

```bash
# Enable model monitoring for Gemini calls
gcloud ai models create justice-ai-gemini-monitored \
    --display-name="Justice AI Gemini" \
    --monitoring-config='{
        "enable_monitoring": true,
        "monitoring_interval_days": 1,
        "enable_fairness_monitoring": true
    }'
```

### Logging Gemini Interactions

```python
from google.cloud import logging as cloud_logging
import json

def log_gemini_interaction(prompt: str, response: str, agent: str):
    """Log all Gemini interactions for audit trail"""
    
    client = cloud_logging.Client()
    logger = client.logger("justice-ai-gemini-interactions")
    
    logger.log_struct(
        {
            "agent": agent,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "timestamp": datetime.now().isoformat(),
            "model": "gemini-1.5-pro"
        },
        severity="INFO"
    )
```

---

## Cost Optimization for Vertex AI

| Optimization | Savings |
|--------------|---------|
| Use Gemini Flash for reporting (State 5) | 50-75% vs Pro |
| Batch predictions for bulk audits | 10-40% volume discount |
| Cache common prompts (100K token cache) | 90% on cached tokens |
| Use embeddings caching | 80% on repeated queries |

---

## Security Best Practices

### 1. API Key Management
```bash
# Store Vertex AI credentials in Secret Manager
echo $(cat service-account-key.json) | \
    gcloud secrets create VERTEX_AI_CREDENTIALS --data-file=-

# Grant service account access
gcloud secrets add-iam-policy-binding VERTEX_AI_CREDENTIALS \
    --member="serviceAccount:justice-ai-sa@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 2. VPC Access
```bash
# Deploy agents with VPC access for secure Vertex AI calls
gcloud run deploy justice-ai-app \
    --vpc-connector=justice-ai-connector \
    --vpc-egress=private-ranges-only
```

### 3. IAM Least Privilege
```bash
# Use minimal role for agents
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:justice-ai-sa@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user" \
    --condition='resource.name.startsWith("projects/PROJECT_ID/locations/us-central1")'
```

---

## Troubleshooting Vertex AI Issues

### Issue: "Resource Not Found" Error

```bash
# Verify Gemini model availability
gcloud ai models list --region=us-central1

# Check quota
gcloud compute project-info describe --project=PROJECT_ID | grep QUOTA
```

### Issue: Vector Search Not Returning Results

```bash
# Check index status
gcloud ai indexes describe justice-ai-legal-precedents \
    --region=us-central1

# Rebuild index if corrupted
gcloud ai indexes update justice-ai-legal-precedents \
    --region=us-central1 \
    --clear-index
```

### Issue: Rate Limiting on Gemini

```python
import time
from google.api_core.exceptions import ResourceExhausted

def call_gemini_with_retry(prompt):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except ResourceExhausted:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
    raise Exception("Rate limit exceeded after retries")
```

---

## Next: Cloud Deployment Script

See `DEPLOYMENT_SCRIPT.ps1` for complete automated setup

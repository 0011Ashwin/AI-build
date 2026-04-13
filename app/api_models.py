"""
API Models — centralised Pydantic request/response schemas for Justice AI backend.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class CaseData(BaseModel):
    case_id: str = Field(..., description="Unique identifier for this audit case")
    name: str = Field(..., description="Subject name (anonymised in reports)")
    age: int = Field(..., ge=0, le=120)
    priors: int = Field(..., ge=0, description="Number of prior convictions / incidents")
    zip_code: str = Field(..., description="Residential zip/postal code (potential proxy variable)")
    original_score: float = Field(..., ge=0, le=100, description="Raw algorithmic score to be audited")
    decision_type: str = Field(..., description="Type of decision: Hiring | Lending | Sentencing | Other")
    jurisdiction: str = Field(..., description="Applicable legal jurisdiction (e.g. 'US Federal', 'California')")
    gender: Optional[str] = Field(None, description="Gender (optional — used in bias group comparisons)")
    race: Optional[str] = Field(None, description="Self-reported race/ethnicity (optional)")
    income_bracket: Optional[str] = Field(None, description="Income bracket (optional)")


class AuditRequest(BaseModel):
    case_data: CaseData


class JurorVote(BaseModel):
    verdict: str  # FAIR | FAIR_WITH_CONCERNS | UNFAIR
    confidence: float
    reasoning: str


class QuantitativeSummary(BaseModel):
    disparate_impact_ratio: Optional[float] = None
    dir_status: Optional[str] = None
    bias_score: Optional[float] = None
    risk_level: Optional[str] = None
    corrected_score: Optional[float] = None
    counterfactual_bias_detected: Optional[bool] = None


class LegalContext(BaseModel):
    bias_type_identified: Optional[str] = None
    top_precedent: Optional[str] = None
    sdg_alignment: Optional[str] = None
    legal_summary: Optional[str] = None


class AuditResponse(BaseModel):
    case_id: str
    verdict: str
    confidence: float
    bias_score: float
    risk_level: str
    corrected_score: float
    report_url: str
    executive_summary: str


class FullReport(BaseModel):
    case_id: str
    case_data: Dict[str, Any]
    verdict: str
    confidence: float
    bias_score: float
    risk_level: str
    corrected_score: float
    juror_votes: Dict[str, Any]
    quantitative_summary: Dict[str, Any]
    legal_context: Dict[str, Any]
    pipeline_stages: List[str]
    executive_summary: str
    generated_at: str
    raw_agent_response: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    agents_loaded: int
    timestamp: str
    shared_modules: bool

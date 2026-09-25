from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ClaimCreate(BaseModel):
    claim_id: str
    scenario_id: str | None = None
    customer_id: str | None = None
    product_id: str | None = None
    product_category: str | None = None
    brand: str | None = None
    model_number: str | None = None
    serial_number: str | None = None
    purchase_date: date | None = None
    claim_date: date | None = None
    fault_date: date | None = None
    warranty_duration_months: int | None = None
    warranty_expiry_date: date | None = None
    warranty_status: str | None = None
    warranty_remaining_days: int | None = None
    extended_warranty: str | None = None
    fault_type: str | None = None
    fault_covered: str | None = None
    damage_type: str | None = None
    claim_reporting_within_period: str | None = None
    claim_amount: float | None = None
    repair_count: int | None = None
    replacement_within_warranty: str | None = None
    required_documents_complete: str | None = None
    purchase_proof_available: str | None = None
    prior_claim_count: int | None = None
    previous_repair_cost: float | None = None
    ocr_confidence: float | None = None
    claim_submission_channel: str | None = None


class ClaimEvidenceCreate(BaseModel):
    receipt_available: str | None = None
    warranty_card_available: str | None = None
    product_image_available: str | None = None
    serial_evidence_available: str | None = None
    fault_evidence_available: str | None = None
    repair_report_available: str | None = None
    previous_repair: str | None = None
    previous_replacement: str | None = None
    serial_number_match: str | None = None
    repair_authorized: str | None = None
    duplicate_claim_indicator: str | None = None
    document_duplicate_indicator: str | None = None
    contradiction_indicator: str | None = None
    document_contradiction_indicator: str | None = None
    product_model_consistent: str | None = None


class ClaimAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_id: int
    ml_prediction: str | None = None
    ml_confidence: float | None = None
    final_decision: str | None = None
    rule_triggered: bool | None = None
    decision_reasons: str | None = None
    analyzed_at: datetime | None = None


class ClaimAnalysisResultResponse(BaseModel):
    claim_id: str
    ml_prediction: str
    ml_confidence: float
    final_decision: str
    rule_triggered: bool
    decision_reasons: list[str]
    analyzed_at: datetime


class ClaimEvidenceResponse(ClaimEvidenceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_id: int


class ClaimResponse(ClaimCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    evidence: ClaimEvidenceResponse | None = None
    analyses: list[ClaimAnalysisResponse] = []


class ClaimListResponse(BaseModel):
    items: list[ClaimResponse]
    page: int
    page_size: int
    total: int

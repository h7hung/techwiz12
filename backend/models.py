from datetime import datetime

from datetime import date

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    scenario_id: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    product_id: Mapped[str | None] = mapped_column(String, nullable=True)
    product_category: Mapped[str | None] = mapped_column(String, nullable=True)
    brand: Mapped[str | None] = mapped_column(String, nullable=True)
    model_number: Mapped[str | None] = mapped_column(String, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String, nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    claim_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fault_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    warranty_duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    warranty_expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    warranty_status: Mapped[str | None] = mapped_column(String, nullable=True)
    warranty_remaining_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extended_warranty: Mapped[str | None] = mapped_column(String, nullable=True)
    fault_type: Mapped[str | None] = mapped_column(String, nullable=True)
    fault_covered: Mapped[str | None] = mapped_column(String, nullable=True)
    damage_type: Mapped[str | None] = mapped_column(String, nullable=True)
    claim_reporting_within_period: Mapped[str | None] = mapped_column(String, nullable=True)
    claim_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    repair_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    replacement_within_warranty: Mapped[str | None] = mapped_column(String, nullable=True)
    required_documents_complete: Mapped[str | None] = mapped_column(String, nullable=True)
    purchase_proof_available: Mapped[str | None] = mapped_column(String, nullable=True)
    prior_claim_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    previous_repair_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    claim_submission_channel: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    evidence: Mapped["ClaimEvidence | None"] = relationship(
        back_populates="claim",
        uselist=False,
        cascade="all, delete-orphan",
    )
    analyses: Mapped[list["ClaimAnalysis"]] = relationship(
        back_populates="claim",
        cascade="all, delete-orphan",
    )


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"), unique=True)
    receipt_available: Mapped[str | None] = mapped_column(String, nullable=True)
    warranty_card_available: Mapped[str | None] = mapped_column(String, nullable=True)
    product_image_available: Mapped[str | None] = mapped_column(String, nullable=True)
    serial_evidence_available: Mapped[str | None] = mapped_column(String, nullable=True)
    fault_evidence_available: Mapped[str | None] = mapped_column(String, nullable=True)
    repair_report_available: Mapped[str | None] = mapped_column(String, nullable=True)
    previous_repair: Mapped[str | None] = mapped_column(String, nullable=True)
    previous_replacement: Mapped[str | None] = mapped_column(String, nullable=True)
    serial_number_match: Mapped[str | None] = mapped_column(String, nullable=True)
    repair_authorized: Mapped[str | None] = mapped_column(String, nullable=True)
    duplicate_claim_indicator: Mapped[str | None] = mapped_column(String, nullable=True)
    document_duplicate_indicator: Mapped[str | None] = mapped_column(String, nullable=True)
    contradiction_indicator: Mapped[str | None] = mapped_column(String, nullable=True)
    document_contradiction_indicator: Mapped[str | None] = mapped_column(String, nullable=True)
    product_model_consistent: Mapped[str | None] = mapped_column(String, nullable=True)

    claim: Mapped[Claim] = relationship(back_populates="evidence")


class ClaimAnalysis(Base):
    __tablename__ = "claim_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"))
    ml_prediction: Mapped[str | None] = mapped_column(String, nullable=True)
    ml_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_decision: Mapped[str | None] = mapped_column(String, nullable=True)
    rule_triggered: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    decision_reasons: Mapped[str | None] = mapped_column(Text, nullable=True)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    claim: Mapped[Claim] = relationship(back_populates="analyses")

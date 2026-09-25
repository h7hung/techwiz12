import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Claim, ClaimAnalysis
from schemas import (
    ClaimAnalysisResultResponse,
    ClaimCreate,
    ClaimListResponse,
    ClaimResponse,
)
from services.decision_service import analyze_claim, serialize_decision_reasons


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.post("", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
def create_claim(claim_data: ClaimCreate, db: Session = Depends(get_db)):
    existing_claim = (
        db.query(Claim).filter(Claim.claim_id == claim_data.claim_id).first()
    )
    if existing_claim is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A claim with this claim_id already exists.",
        )

    claim = Claim(**claim_data.model_dump())
    db.add(claim)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A claim with this claim_id already exists.",
        ) from None

    db.refresh(claim)
    return claim


@router.get("", response_model=ClaimListResponse)
def get_claims(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
):
    total = db.query(Claim).count()
    claims = (
        db.query(Claim)
        .order_by(Claim.created_at.desc(), Claim.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ClaimListResponse(
        items=claims,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if claim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found.",
        )
    return claim


@router.post(
    "/{claim_id}/analyze",
    response_model=ClaimAnalysisResultResponse,
)
def analyze_claim_endpoint(
    claim_id: str,
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if claim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found.",
        )

    try:
        result = analyze_claim(claim)
        analyzed_at = result["analyzed_at"]
        analysis = (
            db.query(ClaimAnalysis)
            .filter(ClaimAnalysis.claim_id == claim.id)
            .order_by(ClaimAnalysis.analyzed_at.desc(), ClaimAnalysis.id.desc())
            .first()
        )

        if analysis is None:
            analysis = ClaimAnalysis(claim_id=claim.id)
            db.add(analysis)

        analysis.ml_prediction = result["ml_prediction"]
        analysis.ml_confidence = result["ml_confidence"]
        analysis.final_decision = result["final_decision"]
        analysis.rule_triggered = result["rule_triggered"]
        analysis.decision_reasons = serialize_decision_reasons(
            result["decision_reasons"]
        )
        analysis.analyzed_at = analyzed_at
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Claim analysis failed for claim_id=%s", claim_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Claim analysis failed.",
        ) from None

    return ClaimAnalysisResultResponse(
        claim_id=claim.claim_id,
        ml_prediction=result["ml_prediction"],
        ml_confidence=result["ml_confidence"],
        final_decision=result["final_decision"],
        rule_triggered=result["rule_triggered"],
        decision_reasons=result["decision_reasons"],
        analyzed_at=analyzed_at,
    )


@router.delete("/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if claim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found.",
        )

    db.delete(claim)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

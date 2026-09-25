import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from models import Claim


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_FILE = PROJECT_ROOT / "model" / "assurex_final_model.joblib"
DECISION_ENGINE_FILE = PROJECT_ROOT / "decision_engine.py"
PREPROCESS_FILE = PROJECT_ROOT / "preprocessing" / "preprocess.py"

IDENTIFIER_COLUMNS = [
    "ClaimID",
    "ScenarioID",
    "CustomerID",
    "ProductID",
    "SerialNumber",
]

RAW_COLUMNS = [
    "ClaimID",
    "ScenarioID",
    "CustomerID",
    "ProductID",
    "ProductCategory",
    "Brand",
    "ModelNumber",
    "SerialNumber",
    "PurchaseDate",
    "ClaimDate",
    "FaultDate",
    "WarrantyDurationMonths",
    "WarrantyExpiryDate",
    "WarrantyStatus",
    "WarrantyRemainingDays",
    "ExtendedWarranty",
    "FaultType",
    "DamageType",
    "FaultCovered",
    "ClaimReportingWithinPeriod",
    "ReceiptAvailable",
    "WarrantyCardAvailable",
    "ProductImageAvailable",
    "SerialEvidenceAvailable",
    "FaultEvidenceAvailable",
    "RepairReportAvailable",
    "PreviousRepair",
    "RepairCount",
    "RepairAuthorized",
    "PreviousReplacement",
    "ReplacementWithinWarranty",
    "SerialNumberMatch",
    "ProductModelConsistent",
    "DuplicateClaimIndicator",
    "DocumentDuplicateIndicator",
    "ContradictionIndicator",
    "DocumentContradictionIndicator",
    "RequiredDocumentsComplete",
    "PurchaseProofAvailable",
    "PriorClaimCount",
    "ClaimAmount",
    "PreviousRepairCost",
    "OCRConfidence",
    "ClaimSubmissionChannel",
]


model = joblib.load(MODEL_FILE)


def _load_existing_business_rules():
    """Load the validated rule function without running evaluation side effects."""
    source = DECISION_ENGINE_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(DECISION_ENGINE_FILE))
    rule_function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "apply_business_rules"
    )
    namespace: dict[str, Any] = {"LOW_CONFIDENCE_THRESHOLD": 0.60}
    function_module = ast.Module(body=[rule_function], type_ignores=[])
    exec(compile(function_module, str(DECISION_ENGINE_FILE), "exec"), namespace)
    return namespace["apply_business_rules"]


def _load_existing_preprocessing():
    """Load the existing feature function without running its file-level jobs."""
    source = PREPROCESS_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(PREPROCESS_FILE))
    date_columns = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "DATE_COLUMNS"
            for target in node.targets
        )
    )
    feature_function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "create_features"
    )
    namespace: dict[str, Any] = {"pd": pd}
    function_module = ast.Module(
        body=[date_columns, feature_function],
        type_ignores=[],
    )
    exec(compile(function_module, str(PREPROCESS_FILE), "exec"), namespace)
    return namespace["create_features"]


apply_business_rules = _load_existing_business_rules()
create_features = _load_existing_preprocessing()


def _build_raw_row(claim: Claim) -> dict[str, Any]:
    evidence = claim.evidence
    row: dict[str, Any] = {column: None for column in RAW_COLUMNS}

    row.update(
        {
            "ClaimID": claim.claim_id,
            "ScenarioID": claim.scenario_id,
            "CustomerID": claim.customer_id,
            "ProductID": claim.product_id,
            "ProductCategory": claim.product_category,
            "Brand": claim.brand,
            "ModelNumber": claim.model_number,
            "SerialNumber": claim.serial_number,
            "PurchaseDate": claim.purchase_date,
            "ClaimDate": claim.claim_date,
            "FaultDate": claim.fault_date,
            "WarrantyDurationMonths": claim.warranty_duration_months,
            "WarrantyExpiryDate": claim.warranty_expiry_date,
            "WarrantyStatus": claim.warranty_status,
            "WarrantyRemainingDays": claim.warranty_remaining_days,
            "ExtendedWarranty": claim.extended_warranty,
            "FaultType": claim.fault_type,
            "FaultCovered": claim.fault_covered,
            "DamageType": claim.damage_type,
            "ClaimReportingWithinPeriod": claim.claim_reporting_within_period,
            "ClaimAmount": claim.claim_amount,
            "RepairCount": claim.repair_count,
            "ReplacementWithinWarranty": claim.replacement_within_warranty,
            "RequiredDocumentsComplete": claim.required_documents_complete,
            "PurchaseProofAvailable": claim.purchase_proof_available,
            "PriorClaimCount": claim.prior_claim_count,
            "PreviousRepairCost": claim.previous_repair_cost,
            "OCRConfidence": claim.ocr_confidence,
            "ClaimSubmissionChannel": claim.claim_submission_channel,
        }
    )

    if evidence is not None:
        row.update(
            {
                "ReceiptAvailable": evidence.receipt_available,
                "WarrantyCardAvailable": evidence.warranty_card_available,
                "ProductImageAvailable": evidence.product_image_available,
                "SerialEvidenceAvailable": evidence.serial_evidence_available,
                "FaultEvidenceAvailable": evidence.fault_evidence_available,
                "RepairReportAvailable": evidence.repair_report_available,
                "PreviousRepair": evidence.previous_repair,
                "PreviousReplacement": evidence.previous_replacement,
                "SerialNumberMatch": evidence.serial_number_match,
                "RepairAuthorized": evidence.repair_authorized,
                "DuplicateClaimIndicator": evidence.duplicate_claim_indicator,
                "DocumentDuplicateIndicator": evidence.document_duplicate_indicator,
                "ContradictionIndicator": evidence.contradiction_indicator,
                "DocumentContradictionIndicator": evidence.document_contradiction_indicator,
                "ProductModelConsistent": evidence.product_model_consistent,
            }
        )

    return row


def analyze_claim(claim_data: Claim) -> dict[str, Any]:
    """Run the saved model and the existing business rules for one claim."""
    raw_row = _build_raw_row(claim_data)
    raw_df = pd.DataFrame([raw_row], columns=RAW_COLUMNS)
    processed_df = create_features(raw_df)
    features = processed_df.drop(columns=["ClaimClass"], errors="ignore")
    features = features.drop(columns=IDENTIFIER_COLUMNS, errors="ignore")

    ml_prediction = str(model.predict(features)[0])
    ml_confidence = float(model.predict_proba(features).max(axis=1)[0])
    final_decision, decision_reasons = apply_business_rules(
        raw_row,
        ml_prediction,
        ml_confidence,
    )

    return {
        "ml_prediction": ml_prediction,
        "ml_confidence": round(ml_confidence, 4),
        "final_decision": final_decision,
        "rule_triggered": bool(decision_reasons),
        "decision_reasons": decision_reasons,
        "analyzed_at": datetime.utcnow(),
    }


def serialize_decision_reasons(reasons: list[str]) -> str:
    return json.dumps(reasons)

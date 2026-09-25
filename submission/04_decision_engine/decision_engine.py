from pathlib import Path

import joblib
import pandas as pd


# =========================================================
# ASSUREX CLAIM DECISION ENGINE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

MODEL_FILE = PROJECT_ROOT / "model" / "assurex_final_model.joblib"
RAW_TEST_FILE = PROJECT_ROOT / "data" / "test" / "assurex_test.csv"
PROCESSED_TEST_FILE = (
    PROJECT_ROOT / "data" / "processed" / "test_processed.csv"
)
OUTPUT_FILE = PROJECT_ROOT / "model" / "decision_engine_test_results.csv"

LOW_CONFIDENCE_THRESHOLD = 0.60


def apply_business_rules(row, ml_prediction, ml_confidence):
    """Apply rules to raw data without changing ML prediction data."""

    hard_invalid_reasons = []
    manual_review_reasons = []
    warning_reasons = []

    # Manual review: uncertainty or incomplete evidence.
    if ml_confidence < LOW_CONFIDENCE_THRESHOLD:
        manual_review_reasons.append("Low ML confidence")

    if str(row.get("RequiredDocumentsComplete", "")).strip().lower() in [
        "no", "false", "0"
    ]:
        manual_review_reasons.append("Missing required documents")

    if str(row.get("ContradictionIndicator", "")).strip().lower() == "yes":
        manual_review_reasons.append("Claim contradiction")

    if str(row.get("DocumentContradictionIndicator", "")).strip().lower() == "yes":
        manual_review_reasons.append("Document contradiction")

    if str(row.get("ProductModelConsistent", "")).strip().lower() == "no":
        manual_review_reasons.append("Product/model inconsistency")

    # Hard invalid: the policy explicitly excludes the claim.
    if str(row.get("DuplicateClaimIndicator", "")).strip().lower() in [
        "yes", "true", "1"
    ]:
        hard_invalid_reasons.append("Duplicate claim")

    if str(row.get("WarrantyStatus", "")).strip().lower() == "expired":
        hard_invalid_reasons.append("Warranty expired")

    if str(row.get("FaultCovered", "")).strip().lower() == "no":
        hard_invalid_reasons.append("Fault not covered")

    # A confirmed mismatch/unauthorized repair is invalid; Unknown needs review.
    serial_status = str(row.get("SerialNumberMatch", "")).strip().lower()
    if serial_status == "no":
        hard_invalid_reasons.append("Serial number mismatch")
    elif serial_status == "unknown":
        manual_review_reasons.append("Serial number verification issue")

    repair_status = str(row.get("RepairAuthorized", "")).strip().lower()
    if repair_status == "no":
        hard_invalid_reasons.append("Unauthorized repair")
    elif repair_status == "unknown":
        manual_review_reasons.append("Repair authorization issue")

    # Informational warning: it must not override the ML decision.
    if str(row.get("DocumentDuplicateIndicator", "")).strip().lower() in [
        "yes", "true", "1"
    ]:
        warning_reasons.append("Duplicate document warning")

    if hard_invalid_reasons:
        final_decision = "Invalid Claim"
        reasons = hard_invalid_reasons + manual_review_reasons + warning_reasons
    elif manual_review_reasons:
        final_decision = "Manual Review"
        reasons = manual_review_reasons + warning_reasons
    else:
        final_decision = ml_prediction
        reasons = warning_reasons

    return final_decision, reasons


print("=" * 70)
print("ASSUREX CLAIM DECISION ENGINE")
print("=" * 70)

print("\n[1] Loading Python ML model...")
model = joblib.load(MODEL_FILE)
print("Model loaded successfully.")

print("\n[2] Loading raw test dataset...")
raw_df = pd.read_csv(RAW_TEST_FILE)
print(f"Raw test claims loaded: {len(raw_df)}")

print("\n[3] Loading processed test dataset...")
processed_df = pd.read_csv(PROCESSED_TEST_FILE)
print(f"Processed test claims loaded: {len(processed_df)}")

if len(raw_df) != len(processed_df):
    raise ValueError(
        "Raw test data and processed test data have different numbers of rows."
    )

# Processed data is used only for ML. No feature engineering is recreated here.
identifier_columns = [
    "ClaimID",
    "ScenarioID",
    "CustomerID",
    "ProductID",
    "SerialNumber",
]

X = processed_df.drop(columns=["ClaimClass"], errors="ignore")
X = X.drop(columns=identifier_columns, errors="ignore")

print(f"\n[4] ML feature columns: {X.shape[1]}")
print("\n[5] Running Python ML predictions...")

predictions = model.predict(X)
probabilities = model.predict_proba(X)
confidence = probabilities.max(axis=1)

print("Python ML prediction completed.")

print("\n[6] Applying business rules...")
results = []

for index, row in raw_df.iterrows():
    ml_prediction = str(predictions[index])
    ml_confidence = float(confidence[index])
    final_decision, reasons = apply_business_rules(
        row,
        ml_prediction,
        ml_confidence,
    )

    results.append(
        {
            "ClaimID": row.get("ClaimID", ""),
            "MLPrediction": ml_prediction,
            "MLConfidence": round(ml_confidence, 4),
            "FinalDecision": final_decision,
            "RuleTriggered": "Yes" if reasons else "No",
            "DecisionReasons": "; ".join(reasons),
            "ActualClass": row.get("ClaimClass", ""),
        }
    )

result_df = pd.DataFrame(results)
result_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

correct = (result_df["FinalDecision"] == result_df["ActualClass"]).sum()
total = len(result_df)
accuracy = correct / total if total else 0

print("\n" + "=" * 70)
print("DECISION ENGINE RESULT")
print("=" * 70)
print("\nFinal Decision distribution:")
print(result_df["FinalDecision"].value_counts())
print("\nML Prediction distribution:")
print(result_df["MLPrediction"].value_counts())
print("\nRule triggered:")
print(result_df["RuleTriggered"].value_counts())
print("\nFinal Decision Accuracy:")
print(f"Correct: {correct}")
print(f"Total  : {total}")
print(f"Accuracy: {accuracy:.2%}")
print("\nOutput:")
print(OUTPUT_FILE)
print("\nCompleted successfully.")

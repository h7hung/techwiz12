import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score


# ============================================================
# ASSUREX CLAIM ENGINE
# FINAL PYTHON MODEL ANALYSIS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "model"
    / "assurex_final_model.joblib"
)

TEST_PATH = (
    BASE_DIR
    / "data"
    / "test"
    / "assurex_test.csv"
)

MODEL_DIR = BASE_DIR / "model"

DATE_COLUMNS = [
    "PurchaseDate",
    "ClaimDate",
    "FaultDate",
    "WarrantyExpiryDate"
]


def create_features(df):

    df = df.copy()

    for column in DATE_COLUMNS:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    df["ProductAgeDays"] = (
        df["ClaimDate"]
        - df["PurchaseDate"]
    ).dt.days

    df["WarrantyRemainingDays"] = (
        df["WarrantyExpiryDate"]
        - df["ClaimDate"]
    ).dt.days

    document_columns = [
        "ReceiptAvailable",
        "WarrantyCardAvailable",
        "ProductImageAvailable",
        "SerialEvidenceAvailable",
        "FaultEvidenceAvailable",
        "RepairReportAvailable"
    ]

    df["MissingDocumentCount"] = (
        df[document_columns]
        .apply(
            lambda row: sum(value == "No" for value in row),
            axis=1
        )
    )

    df["ClaimReportingDelayDays"] = (
        df["ClaimDate"]
        - df["FaultDate"]
    ).dt.days

    df["HasRepairHistory"] = (
        df["PreviousRepair"]
        .map({"Yes": 1, "No": 0})
        .fillna(0)
    )

    df["HasPreviousReplacement"] = (
        df["PreviousReplacement"]
        .map({"Yes": 1, "No": 0})
        .fillna(0)
    )

    return df.drop(columns=DATE_COLUMNS)


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 70)
print("ASSUREX CLAIM ENGINE")
print("FINAL PYTHON MODEL ANALYSIS")
print("=" * 70)

model = joblib.load(MODEL_PATH)

test_df = pd.read_csv(TEST_PATH)
test_processed = create_features(test_df)


# ============================================================
# PREPARE TEST DATA
# ============================================================

TARGET = "ClaimClass"

DROP_COLUMNS = [
    "ClaimID",
    "ScenarioID",
    "CustomerID",
    "ProductID",
    "SerialNumber"
]

X_test = test_processed.drop(
    columns=[TARGET] + DROP_COLUMNS,
    errors="ignore"
)

y_test = test_df[TARGET]


# ============================================================
# PREDICTION
# ============================================================

predictions = model.predict(X_test)

probabilities = model.predict_proba(X_test)

classes = model.named_steps[
    "classifier"
].classes_


accuracy = accuracy_score(
    y_test,
    predictions
)


print("\n")
print("=" * 70)
print("FINAL MODEL")
print("=" * 70)

print(
    "Model:",
    model.named_steps["classifier"]
)

print(
    f"Test Accuracy: {accuracy:.4f}"
)


# ============================================================
# CONFIDENCE DISTRIBUTION
# ============================================================

print("\n")
print("=" * 70)
print("CONFIDENCE ANALYSIS")
print("=" * 70)

for index, class_name in enumerate(classes):

    confidence = probabilities[:, index]

    print(
        f"\n{class_name}"
    )

    print(
        f"Minimum : {confidence.min():.4f}"
    )

    print(
        f"Maximum : {confidence.max():.4f}"
    )

    print(
        f"Average : {confidence.mean():.4f}"
    )


# ============================================================
# SAVE FULL TEST PREDICTIONS
# ============================================================

prediction_df = test_df[
    [
        "ClaimID",
        "ClaimClass"
    ]
].copy()

prediction_df["PredictedClass"] = predictions


for index, class_name in enumerate(classes):

    column_name = (
        "Confidence_"
        + class_name.replace(" ", "_")
    )

    prediction_df[column_name] = (
        probabilities[:, index]
    )


prediction_df["TopConfidence"] = (
    probabilities.max(axis=1)
)

prediction_df["CorrectPrediction"] = (
    prediction_df["ClaimClass"]
    == prediction_df["PredictedClass"]
)


prediction_path = (
    MODEL_DIR
    / "full_test_predictions.csv"
)

prediction_df.to_csv(
    prediction_path,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# LOW CONFIDENCE CASES
# ============================================================

LOW_CONFIDENCE_THRESHOLD = 0.60

low_confidence_df = (
    prediction_df[
        prediction_df["TopConfidence"]
        < LOW_CONFIDENCE_THRESHOLD
    ]
)


print("\n")
print("=" * 70)
print("LOW CONFIDENCE CASES")
print("=" * 70)

print(
    f"Threshold: "
    f"{LOW_CONFIDENCE_THRESHOLD}"
)

print(
    f"Number of low-confidence claims: "
    f"{len(low_confidence_df)}"
)


low_confidence_path = (
    MODEL_DIR
    / "low_confidence_claims.csv"
)

low_confidence_df.to_csv(
    low_confidence_path,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# PERMUTATION IMPORTANCE
# ============================================================

print("\n")
print("=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

print(
    "Calculating permutation importance..."
)


importance_result = permutation_importance(
    model,
    X_test,
    y_test,
    n_repeats=5,
    random_state=20260924,
    scoring="f1_macro",
    n_jobs=-1
)


importance_df = pd.DataFrame(
    {
        "Feature": X_test.columns,
        "ImportanceMean":
            importance_result.importances_mean,
        "ImportanceStd":
            importance_result.importances_std
    }
)


importance_df = importance_df.sort_values(
    by="ImportanceMean",
    ascending=False
)


print(
    importance_df.head(15).to_string(
        index=False
    )
)


importance_path = (
    MODEL_DIR
    / "feature_importance.csv"
)

importance_df.to_csv(
    importance_path,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# FINISH
# ============================================================

print("\n")
print("=" * 70)
print("MODEL ANALYSIS COMPLETED")
print("=" * 70)

print(
    "Generated:"
)

print(
    prediction_path
)

print(
    low_confidence_path
)

print(
    importance_path
)

print("=" * 70)
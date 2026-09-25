import pandas as pd
import numpy as np

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# ASSUREX CLAIM ENGINE
# ROBUSTNESS TEST
# ============================================================

print("=" * 70)
print("ASSUREX CLAIM ENGINE")
print("PYTHON ML ROBUSTNESS TEST")
print("=" * 70)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 20260924

TRAIN_PATH = Path("data/processed/train_processed.csv")
VALIDATION_PATH = Path("data/processed/validation_processed.csv")
TEST_PATH = Path("data/processed/test_processed.csv")

OUTPUT_PATH = Path("model/robustness_comparison.csv")


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading datasets...")

train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)
test_df = pd.read_csv(TEST_PATH)

print(f"Train      : {len(train_df)} records")
print(f"Validation : {len(validation_df)} records")
print(f"Test       : {len(test_df)} records")


# ============================================================
# TARGET
# ============================================================

TARGET = "ClaimClass"


y_train = train_df[TARGET]
y_validation = validation_df[TARGET]
y_test = test_df[TARGET]


# ============================================================
# IDENTIFIER COLUMNS
# ============================================================

IDENTIFIER_COLUMNS = [
    "ClaimID",
    "ScenarioID",
    "CustomerID",
    "ProductID",
    "ModelNumber",
    "SerialNumber"
]


# ============================================================
# RULE-DERIVED / DIRECT DECISION FEATURES
# ============================================================

RULE_DERIVED_FEATURES = [
    "WarrantyStatus",
    "FaultCovered",
    "ClaimReportingWithinPeriod",
    "RepairAuthorized",
    "SerialNumberMatch",
    "RequiredDocumentsComplete"
]


# ============================================================
# MODEL COLUMNS
# ============================================================

ALL_DROP_COLUMNS = [
    TARGET
] + IDENTIFIER_COLUMNS


# ============================================================
# PREPROCESSOR CREATOR
# ============================================================

def create_pipeline(X):

    numerical_features = X.select_dtypes(
        include=[
            "int64",
            "int32",
            "float64",
            "float32"
        ]
    ).columns.tolist()

    categorical_features = X.select_dtypes(
        include=[
            "object",
            "category",
            "bool"
        ]
    ).columns.tolist()

    numerical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median")
            ),
            (
                "scaler",
                StandardScaler()
            )
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False
                )
            )
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                numerical_pipeline,
                numerical_features
            ),
            (
                "cat",
                categorical_pipeline,
                categorical_features
            )
        ]
    )

    model = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=3,
        random_state=RANDOM_STATE
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "classifier",
                model
            )
        ]
    )

    return pipeline


# ============================================================
# MODEL EVALUATION
# ============================================================

def evaluate_model(
    model_name,
    X_train,
    y_train,
    X_validation,
    y_validation,
    X_test,
    y_test
):

    print("\n")
    print("=" * 70)
    print(f"MODEL: {model_name}")
    print("=" * 70)

    print("\nTraining...")

    pipeline = create_pipeline(X_train)

    pipeline.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    validation_prediction = pipeline.predict(
        X_validation
    )

    validation_accuracy = accuracy_score(
        y_validation,
        validation_prediction
    )

    validation_precision = precision_score(
        y_validation,
        validation_prediction,
        average="macro",
        zero_division=0
    )

    validation_recall = recall_score(
        y_validation,
        validation_prediction,
        average="macro",
        zero_division=0
    )

    validation_f1 = f1_score(
        y_validation,
        validation_prediction,
        average="macro",
        zero_division=0
    )

    print("\nValidation Results")

    print(
        f"Accuracy  : {validation_accuracy:.4f}"
    )

    print(
        f"Precision : {validation_precision:.4f}"
    )

    print(
        f"Recall    : {validation_recall:.4f}"
    )

    print(
        f"F1-score  : {validation_f1:.4f}"
    )


    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    test_prediction = pipeline.predict(
        X_test
    )

    test_accuracy = accuracy_score(
        y_test,
        test_prediction
    )

    test_precision = precision_score(
        y_test,
        test_prediction,
        average="macro",
        zero_division=0
    )

    test_recall = recall_score(
        y_test,
        test_prediction,
        average="macro",
        zero_division=0
    )

    test_f1 = f1_score(
        y_test,
        test_prediction,
        average="macro",
        zero_division=0
    )

    print("\nTest Results")

    print(
        f"Accuracy  : {test_accuracy:.4f}"
    )

    print(
        f"Precision : {test_precision:.4f}"
    )

    print(
        f"Recall    : {test_recall:.4f}"
    )

    print(
        f"F1-score  : {test_f1:.4f}"
    )


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {
        "Model": model_name,

        "Validation_Accuracy":
            validation_accuracy,

        "Validation_Precision":
            validation_precision,

        "Validation_Recall":
            validation_recall,

        "Validation_F1":
            validation_f1,

        "Test_Accuracy":
            test_accuracy,

        "Test_Precision":
            test_precision,

        "Test_Recall":
            test_recall,

        "Test_F1":
            test_f1
    }


# ============================================================
# BASE DATA
# ============================================================

X_train_base = train_df.drop(
    columns=ALL_DROP_COLUMNS,
    errors="ignore"
)

X_validation_base = validation_df.drop(
    columns=ALL_DROP_COLUMNS,
    errors="ignore"
)

X_test_base = test_df.drop(
    columns=ALL_DROP_COLUMNS,
    errors="ignore"
)


# ============================================================
# MODEL A
# ALL NORMAL FEATURES
# ============================================================

results = []

result_a = evaluate_model(
    "Model A - All Features",
    X_train_base,
    y_train,
    X_validation_base,
    y_validation,
    X_test_base,
    y_test
)

results.append(result_a)


# ============================================================
# MODEL B
# REMOVE RULE-DERIVED FEATURES
# ============================================================

print("\n")
print("=" * 70)
print("MODEL B FEATURE REMOVAL")
print("=" * 70)

print("\nRemoving:")

for feature in RULE_DERIVED_FEATURES:
    print(f" - {feature}")


X_train_b = X_train_base.drop(
    columns=RULE_DERIVED_FEATURES,
    errors="ignore"
)

X_validation_b = X_validation_base.drop(
    columns=RULE_DERIVED_FEATURES,
    errors="ignore"
)

X_test_b = X_test_base.drop(
    columns=RULE_DERIVED_FEATURES,
    errors="ignore"
)


result_b = evaluate_model(
    "Model B - Without Rule Features",
    X_train_b,
    y_train,
    X_validation_b,
    y_validation,
    X_test_b,
    y_test
)

results.append(result_b)


# ============================================================
# MODEL C
# CORE CLAIM FEATURES
# ============================================================

CORE_FEATURES = [
    "ProductCategory",
    "Brand",
    "WarrantyDurationMonths",
    "ExtendedWarranty",
    "FaultType",
    "DamageType",
    "ReceiptAvailable",
    "WarrantyCardAvailable",
    "ProductImageAvailable",
    "SerialEvidenceAvailable",
    "FaultEvidenceAvailable",
    "RepairReportAvailable",
    "PreviousRepair",
    "RepairCount",
    "PreviousReplacement",
    "ReplacementWithinWarranty",
    "ProductModelConsistent",
    "DuplicateClaimIndicator",
    "DocumentDuplicateIndicator",
    "ContradictionIndicator",
    "PurchaseProofAvailable",
    "PriorClaimCount",
    "ClaimAmount",
    "PreviousRepairCost",
    "OCRConfidence",
    "ClaimSubmissionChannel",
    "ProductAgeDays",
    "MissingDocumentCount",
    "ClaimReportingDelayDays",
    "HasRepairHistory",
    "HasPreviousReplacement"
]


available_core_features = [
    feature
    for feature in CORE_FEATURES
    if feature in X_train_base.columns
]


print("\n")
print("=" * 70)
print("MODEL C CORE FEATURES")
print("=" * 70)

print(
    f"\nUsing {len(available_core_features)} core features:"
)

for feature in available_core_features:
    print(f" - {feature}")


X_train_c = X_train_base[
    available_core_features
].copy()

X_validation_c = X_validation_base[
    available_core_features
].copy()

X_test_c = X_test_base[
    available_core_features
].copy()


result_c = evaluate_model(
    "Model C - Core Features",
    X_train_c,
    y_train,
    X_validation_c,
    y_validation,
    X_test_c,
    y_test
)

results.append(result_c)


# ============================================================
# COMPARISON TABLE
# ============================================================

comparison = pd.DataFrame(results)


print("\n")
print("=" * 70)
print("ROBUSTNESS COMPARISON")
print("=" * 70)

print(
    comparison.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# SAVE
# ============================================================

comparison.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# DIFFERENCE ANALYSIS
# ============================================================

print("\n")
print("=" * 70)
print("ROBUSTNESS ANALYSIS")
print("=" * 70)


base_test_f1 = result_a["Test_F1"]

model_b_difference = (
    result_b["Test_F1"] - base_test_f1
)

model_c_difference = (
    result_c["Test_F1"] - base_test_f1
)


print(
    f"\nModel A Test F1: "
    f"{base_test_f1:.4f}"
)

print(
    f"Model B Test F1 difference: "
    f"{model_b_difference:+.4f}"
)

print(
    f"Model C Test F1 difference: "
    f"{model_c_difference:+.4f}"
)


# ============================================================
# INTERPRETATION
# ============================================================

print("\n")
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)


if result_b["Test_F1"] >= 0.95:

    print(
        "\nModel B remains >= 0.95 F1."
    )

    print(
        "The model retains strong performance "
        "even without the main rule-derived features."
    )

else:

    print(
        "\nModel B drops below 0.95 F1."
    )

    print(
        "The current dataset appears to depend "
        "strongly on rule-derived features."
    )


if result_c["Test_F1"] >= 0.90:

    print(
        "\nModel C remains >= 0.90 F1."
    )

    print(
        "Core claim information still provides "
        "strong predictive signal."
    )

else:

    print(
        "\nModel C drops below 0.90 F1."
    )

    print(
        "The dataset may be highly dependent "
        "on direct decision features."
    )


# ============================================================
# FINAL
# ============================================================

print("\n")
print("=" * 70)
print("ROBUSTNESS TEST COMPLETED")
print("=" * 70)

print(
    f"\nSaved comparison:"
)

print(
    OUTPUT_PATH
)

print(
    "\nNext step:"
)

print(
    "Review Model A, B and C before finalizing Python ML."
)

print("=" * 70)
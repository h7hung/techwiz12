import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)

from sklearn.model_selection import (
    cross_validate,
    StratifiedKFold
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# ASSUREX CLAIM ENGINE
# PYTHON MACHINE LEARNING
# MODEL COMPARISON
# ============================================================


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"

TRAIN_PATH = DATA_DIR / "train_processed.csv"
VALIDATION_PATH = DATA_DIR / "validation_processed.csv"
TEST_PATH = DATA_DIR / "test_processed.csv"

MODEL_DIR = BASE_DIR / "model"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("ASSUREX CLAIM ENGINE")
print("PYTHON ML MODEL TRAINING")
print("=" * 70)

print("\nLoading datasets...")

train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)
test_df = pd.read_csv(TEST_PATH)

print(
    f"Train      : {len(train_df)} records"
)

print(
    f"Validation : {len(validation_df)} records"
)

print(
    f"Test       : {len(test_df)} records"
)


# ============================================================
# 3. TARGET
# ============================================================

TARGET = "ClaimClass"


y_train = train_df[TARGET]
y_validation = validation_df[TARGET]
y_test = test_df[TARGET]


X_train = train_df.drop(
    columns=[TARGET]
)

X_validation = validation_df.drop(
    columns=[TARGET]
)

X_test = test_df.drop(
    columns=[TARGET]
)


# ============================================================
# 4. REMOVE IDENTIFIERS / METADATA
# ============================================================

DROP_COLUMNS = [
    "ClaimID",
    "ScenarioID",
    "CustomerID",
    "ProductID",
    "ModelNumber",
    "SerialNumber"
]


X_train = X_train.drop(
    columns=DROP_COLUMNS,
    errors="ignore"
)

X_validation = X_validation.drop(
    columns=DROP_COLUMNS,
    errors="ignore"
)

X_test = X_test.drop(
    columns=DROP_COLUMNS,
    errors="ignore"
)


# ============================================================
# 5. IDENTIFY NUMERICAL / CATEGORICAL FEATURES
# ============================================================

NUMERICAL_FEATURES = X_train.select_dtypes(
    include=[
        "int64",
        "float64"
    ]
).columns.tolist()


CATEGORICAL_FEATURES = X_train.select_dtypes(
    include=[
        "object"
    ]
).columns.tolist()


print("\n")
print("=" * 70)
print("FEATURE INFORMATION")
print("=" * 70)

print(
    f"Numerical features   : "
    f"{len(NUMERICAL_FEATURES)}"
)

for feature in NUMERICAL_FEATURES:

    print(
        f"  NUM - {feature}"
    )


print(
    f"\nCategorical features : "
    f"{len(CATEGORICAL_FEATURES)}"
)

for feature in CATEGORICAL_FEATURES:

    print(
        f"  CAT - {feature}"
    )


# ============================================================
# 6. PREPROCESSING PIPELINE
# ============================================================

NUMERICAL_PIPELINE = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)


CATEGORICAL_PIPELINE = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
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


PREPROCESSOR = ColumnTransformer(
    transformers=[
        (
            "numerical",
            NUMERICAL_PIPELINE,
            NUMERICAL_FEATURES
        ),
        (
            "categorical",
            CATEGORICAL_PIPELINE,
            CATEGORICAL_FEATURES
        )
    ],
    remainder="drop"
)


# ============================================================
# 7. DEFINE THREE ML ALGORITHMS
# ============================================================

MODELS = {

    "Logistic Regression":
        LogisticRegression(
            max_iter=2000,
            random_state=20260924
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=20260924,
            n_jobs=-1
        ),

    "Gradient Boosting":
        GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=3,
            random_state=20260924
        )
}


# ============================================================
# 8. CROSS VALIDATION CONFIGURATION
# ============================================================

CV = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=20260924
)


SCORING = [
    "accuracy",
    "precision_macro",
    "recall_macro",
    "f1_macro"
]


# ============================================================
# 9. TRAIN AND COMPARE MODELS
# ============================================================

results = []

trained_pipelines = {}


for model_name, model in MODELS.items():

    print("\n")
    print("=" * 70)
    print(f"MODEL: {model_name}")
    print("=" * 70)

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                PREPROCESSOR
            ),
            (
                "classifier",
                model
            )
        ]
    )

    print("\nTraining...")

    pipeline.fit(
        X_train,
        y_train
    )

    trained_pipelines[
        model_name
    ] = pipeline

    # --------------------------------------------------------
    # Validation prediction
    # --------------------------------------------------------

    validation_prediction = (
        pipeline.predict(
            X_validation
        )
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
        f"Accuracy  : "
        f"{validation_accuracy:.4f}"
    )

    print(
        f"Precision : "
        f"{validation_precision:.4f}"
    )

    print(
        f"Recall    : "
        f"{validation_recall:.4f}"
    )

    print(
        f"F1-score  : "
        f"{validation_f1:.4f}"
    )


    # --------------------------------------------------------
    # Cross validation
    # --------------------------------------------------------

    print("\n5-Fold Cross Validation...")

    cv_result = cross_validate(
        pipeline,
        X_train,
        y_train,
        cv=CV,
        scoring=SCORING,
        n_jobs=-1
    )

    cv_accuracy = (
        cv_result[
            "test_accuracy"
        ].mean()
    )

    cv_precision = (
        cv_result[
            "test_precision_macro"
        ].mean()
    )

    cv_recall = (
        cv_result[
            "test_recall_macro"
        ].mean()
    )

    cv_f1 = (
        cv_result[
            "test_f1_macro"
        ].mean()
    )


    print(
        f"CV Accuracy  : "
        f"{cv_accuracy:.4f}"
    )

    print(
        f"CV Precision : "
        f"{cv_precision:.4f}"
    )

    print(
        f"CV Recall    : "
        f"{cv_recall:.4f}"
    )

    print(
        f"CV F1        : "
        f"{cv_f1:.4f}"
    )


    results.append(
        {
            "Model": model_name,

            "Validation_Accuracy":
                validation_accuracy,

            "Validation_Precision":
                validation_precision,

            "Validation_Recall":
                validation_recall,

            "Validation_F1":
                validation_f1,

            "CV_Accuracy":
                cv_accuracy,

            "CV_Precision":
                cv_precision,

            "CV_Recall":
                cv_recall,

            "CV_F1":
                cv_f1
        }
    )


# ============================================================
# 10. MODEL COMPARISON TABLE
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    by="Validation_F1",
    ascending=False
)


print("\n")
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x:
            f"{x:.4f}"
    )
)


# ============================================================
# 11. SELECT BEST MODEL
# ============================================================

best_model_name = (
    results_df.iloc[0]["Model"]
)


best_pipeline = (
    trained_pipelines[
        best_model_name
    ]
)


print("\n")
print("=" * 70)
print("SELECTED MODEL")
print("=" * 70)

print(
    f"Selected model: "
    f"{best_model_name}"
)


# ============================================================
# 12. FINAL TEST EVALUATION
# ============================================================

print("\n")
print("=" * 70)
print("FINAL TEST EVALUATION")
print("=" * 70)

test_prediction = (
    best_pipeline.predict(
        X_test
    )
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


print(
    f"Accuracy  : "
    f"{test_accuracy:.4f}"
)

print(
    f"Precision : "
    f"{test_precision:.4f}"
)

print(
    f"Recall    : "
    f"{test_recall:.4f}"
)

print(
    f"F1-score  : "
    f"{test_f1:.4f}"
)


# ============================================================
# 13. CLASSIFICATION REPORT
# ============================================================

print("\n")
print("=" * 70)
print("CLASS-WISE PERFORMANCE")
print("=" * 70)

print(
    classification_report(
        y_test,
        test_prediction,
        zero_division=0
    )
)


# ============================================================
# 14. CONFUSION MATRIX
# ============================================================

labels = [
    "Valid Claim",
    "Invalid Claim",
    "Manual Review"
]


cm = confusion_matrix(
    y_test,
    test_prediction,
    labels=labels
)


cm_df = pd.DataFrame(
    cm,
    index=labels,
    columns=labels
)


print("\n")
print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print(cm_df)


# ============================================================
# 15. SAVE RESULTS
# ============================================================

results_path = (
    MODEL_DIR
    / "model_comparison.csv"
)

results_df.to_csv(
    results_path,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 16. SAVE CONFUSION MATRIX
# ============================================================

confusion_path = (
    MODEL_DIR
    / "confusion_matrix.csv"
)

cm_df.to_csv(
    confusion_path,
    encoding="utf-8-sig"
)


# ============================================================
# 17. SAVE BEST MODEL
# ============================================================

model_path = (
    MODEL_DIR
    / "assurex_final_model.joblib"
)

joblib.dump(
    best_pipeline,
    model_path
)


# ============================================================
# 18. SAVE MODEL INFORMATION
# ============================================================

model_info = pd.DataFrame(
    [
        {
            "ModelVersion":
                "AssureX-Python-ML-v1.0",

            "SelectedModel":
                best_model_name,

            "TestAccuracy":
                test_accuracy,

            "TestPrecision":
                test_precision,

            "TestRecall":
                test_recall,

            "TestF1":
                test_f1,

            "TrainingRecords":
                len(X_train),

            "ValidationRecords":
                len(X_validation),

            "TestRecords":
                len(X_test),

            "RandomSeed":
                20260924
        }
    ]
)


model_info.to_csv(
    MODEL_DIR
    / "model_info.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 19. SAMPLE TEST PREDICTIONS
# ============================================================

test_probabilities = (
    best_pipeline.predict_proba(
        X_test
    )
)

classes = (
    best_pipeline
    .named_steps["classifier"]
    .classes_
)


sample_predictions = test_df[
    [
        "ClaimID",
        "ClaimClass"
    ]
].copy()


sample_predictions[
    "PredictedClass"
] = test_prediction


for index, class_name in enumerate(
    classes
):

    safe_name = (
        class_name
        .replace(" ", "_")
    )

    sample_predictions[
        f"Confidence_{safe_name}"
    ] = test_probabilities[
        :,
        index
    ]


sample_predictions_path = (
    MODEL_DIR
    / "sample_test_predictions.csv"
)


sample_predictions.to_csv(
    sample_predictions_path,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 20. FINISH
# ============================================================

print("\n")
print("=" * 70)
print("PYTHON ML TRAINING COMPLETED")
print("=" * 70)

print(
    f"Selected model : "
    f"{best_model_name}"
)

print(
    f"Test Accuracy  : "
    f"{test_accuracy:.4f}"
)

print(
    f"Test F1        : "
    f"{test_f1:.4f}"
)

print("\nGenerated files:")

print(
    MODEL_DIR /
    "model_comparison.csv"
)

print(
    MODEL_DIR /
    "confusion_matrix.csv"
)

print(
    MODEL_DIR /
    "assurex_final_model.joblib"
)

print(
    MODEL_DIR /
    "model_info.csv"
)

print(
    MODEL_DIR /
    "sample_test_predictions.csv"
)

print("=" * 70)
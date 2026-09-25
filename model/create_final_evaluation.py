from pathlib import Path

import pandas as pd


# =========================================================
# FILES
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "model"

MODEL_COMPARISON_FILE = MODEL_DIR / "model_comparison.csv"
DECISION_AUDIT_FILE = MODEL_DIR / "decision_engine_audit.csv"
MODEL_INFO_FILE = MODEL_DIR / "model_info.csv"

GTM_FILE_NAMES = [
    "validation_predictions.csv",
    "validation_confusion_matrix.csv",
    "test_predictions.csv",
    "test_confusion_matrix.csv",
]

COMPARISON_OUTPUT = MODEL_DIR / "final_model_comparison.csv"
REPORT_OUTPUT = MODEL_DIR / "final_evaluation_report.txt"


# =========================================================
# FIND GTM FILES
# =========================================================

found_gtm_files = {}

for file_name in GTM_FILE_NAMES:
    matches = list(PROJECT_ROOT.rglob(file_name))

    if matches:
        found_gtm_files[file_name] = matches[0]

print("GTM files found:")
for file_name in GTM_FILE_NAMES:
    if file_name in found_gtm_files:
        print(found_gtm_files[file_name])
    else:
        print(f"MISSING: {file_name}")


# =========================================================
# LOAD EXISTING RESULTS
# =========================================================

python_comparison = pd.read_csv(MODEL_COMPARISON_FILE)
decision_audit = pd.read_csv(DECISION_AUDIT_FILE)

model_info = None
if MODEL_INFO_FILE.exists():
    model_info = pd.read_csv(MODEL_INFO_FILE)


# =========================================================
# GTM METRIC HELPERS
# =========================================================

def find_column(dataframe, candidates):
    """Return the first matching column, ignoring case and punctuation."""

    normalized_columns = {
        "".join(character for character in column.lower() if character.isalnum()): column
        for column in dataframe.columns
    }

    for candidate in candidates:
        normalized_candidate = "".join(
            character for character in candidate.lower()
            if character.isalnum()
        )

        if normalized_candidate in normalized_columns:
            return normalized_columns[normalized_candidate]

    return None


def calculate_prediction_metrics(file_path):
    """Calculate metrics from a GTM prediction CSV."""

    dataframe = pd.read_csv(file_path)

    actual_column = find_column(
        dataframe,
        [
            "ActualClass",
            "Actual",
            "TrueClass",
            "TrueLabel",
            "Label",
            "ClaimClass",
            "y_true",
        ],
    )

    predicted_column = find_column(
        dataframe,
        [
            "PredictedClass",
            "Predicted",
            "Prediction",
            "PredictedLabel",
            "y_pred",
        ],
    )

    if actual_column is None or predicted_column is None:
        raise ValueError(
            f"Could not find actual/prediction columns in {file_path}"
        )

    actual = dataframe[actual_column]
    predicted = dataframe[predicted_column]

    labels = sorted(set(actual) | set(predicted))
    precision_values = []
    recall_values = []
    f1_values = []

    for label in labels:
        true_positive = ((actual == label) & (predicted == label)).sum()
        false_positive = ((actual != label) & (predicted == label)).sum()
        false_negative = ((actual == label) & (predicted != label)).sum()

        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0
        )
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0
        )

        precision_values.append(precision)
        recall_values.append(recall)
        f1_values.append(f1)

    return {
        "accuracy": (actual == predicted).mean(),
        "precision": sum(precision_values) / len(precision_values),
        "recall": sum(recall_values) / len(recall_values),
        "f1": sum(f1_values) / len(f1_values),
        "rows": len(dataframe),
    }


def read_gtm_file(file_path):
    """Read a GTM CSV so every found evaluation file is consumed."""

    return pd.read_csv(file_path)


# Read every found GTM file. Confusion matrices are retained for report context;
# prediction files provide the labels needed for metric calculation.
gtm_data = {}
for file_name, file_path in found_gtm_files.items():
    gtm_data[file_name] = read_gtm_file(file_path)


gtm_metrics = {}
gtm_errors = []

for file_name in GTM_FILE_NAMES:
    if file_name not in found_gtm_files:
        gtm_errors.append(f"Missing {file_name}")

for split in ["validation", "test"]:
    prediction_name = f"{split}_predictions.csv"

    if prediction_name not in found_gtm_files:
        continue

    try:
        gtm_metrics[split] = calculate_prediction_metrics(
            found_gtm_files[prediction_name]
        )
    except ValueError as error:
        gtm_errors.append(str(error))


# =========================================================
# FINAL MODEL COMPARISON
# =========================================================

model_names = [
    "Logistic Regression",
    "Random Forest",
    "Gradient Boosting",
]

comparison_rows = []

for model_name in model_names:
    matching_rows = python_comparison[
        python_comparison["Model"] == model_name
    ]

    row = {
        "Model": model_name,
        "Validation_F1": "",
        "Test_Accuracy": "",
        "Test_Precision": "",
        "Test_Recall": "",
        "Test_F1": "",
        "Notes": "",
    }

    if not matching_rows.empty:
        source_row = matching_rows.iloc[0]
        row["Validation_F1"] = source_row.get("Validation_F1", "")

    if model_info is not None and not model_info.empty:
        selected_model = model_info.iloc[0]["SelectedModel"]

        if model_name == selected_model:
            source_row = model_info.iloc[0]
            row["Test_Accuracy"] = source_row.get("TestAccuracy", "")
            row["Test_Precision"] = source_row.get("TestPrecision", "")
            row["Test_Recall"] = source_row.get("TestRecall", "")
            row["Test_F1"] = source_row.get("TestF1", "")
            row["Notes"] = "Test metrics from model_info.csv"
        else:
            row["Notes"] = "Individual test metrics not available"
    else:
        row["Notes"] = "Individual test metrics not available"

    comparison_rows.append(row)


gtm_row = {
    "Model": "GTM",
    "Validation_F1": "",
    "Test_Accuracy": "",
    "Test_Precision": "",
    "Test_Recall": "",
    "Test_F1": "",
    "Notes": "; ".join(gtm_errors),
}

if "validation" in gtm_metrics:
    gtm_row["Validation_F1"] = gtm_metrics["validation"]["f1"]

if "test" in gtm_metrics:
    gtm_row["Test_Accuracy"] = gtm_metrics["test"]["accuracy"]
    gtm_row["Test_Precision"] = gtm_metrics["test"]["precision"]
    gtm_row["Test_Recall"] = gtm_metrics["test"]["recall"]
    gtm_row["Test_F1"] = gtm_metrics["test"]["f1"]

if not gtm_errors:
    gtm_row["Notes"] = "Metrics calculated from GTM prediction files"

comparison_rows.append(gtm_row)

comparison_df = pd.DataFrame(comparison_rows)
comparison_df.to_csv(COMPARISON_OUTPUT, index=False, encoding="utf-8-sig")


# =========================================================
# DECISION ENGINE METRICS
# =========================================================

final_accuracy_rows = decision_audit[
    decision_audit["Metric"] == "FinalAccuracy"
]

final_accuracy = ""
if not final_accuracy_rows.empty:
    final_accuracy = final_accuracy_rows.iloc[0]["Count"]

final_decision_rows = decision_audit[
    decision_audit["Metric"] == "FinalDecision"
]

total_claims = final_decision_rows["Count"].sum()
correct_final_decisions = ""
wrong_final_decisions = ""

if final_accuracy != "" and total_claims:
    correct_final_decisions = round(float(final_accuracy) * total_claims)
    wrong_final_decisions = total_claims - correct_final_decisions

low_confidence_rows = decision_audit[
    (decision_audit["Metric"] == "DecisionReason")
    & (decision_audit["Category"] == "Low ML confidence")
]

low_confidence_count = 0
if not low_confidence_rows.empty:
    low_confidence_count = low_confidence_rows.iloc[0]["Count"]


# =========================================================
# TEXT REPORT
# =========================================================

report_lines = []
report_lines.append("ASSUREX FINAL EVALUATION REPORT")
report_lines.append("=" * 70)
report_lines.append("")

report_lines.append("PYTHON ML MODEL COMPARISON")
report_lines.append("-" * 70)
report_lines.append(comparison_df.iloc[:3].to_string(index=False))
report_lines.append("")

report_lines.append("GTM VALIDATION RESULTS")
report_lines.append("-" * 70)
if "validation" in gtm_metrics:
    metrics = gtm_metrics["validation"]
    report_lines.append(f"Accuracy: {metrics['accuracy']:.6f}")
    report_lines.append(f"Macro precision: {metrics['precision']:.6f}")
    report_lines.append(f"Macro recall: {metrics['recall']:.6f}")
    report_lines.append(f"Macro F1: {metrics['f1']:.6f}")
else:
    report_lines.append("Metrics unavailable.")
report_lines.append("")

report_lines.append("GTM TEST RESULTS")
report_lines.append("-" * 70)
if "test" in gtm_metrics:
    metrics = gtm_metrics["test"]
    report_lines.append(f"Accuracy: {metrics['accuracy']:.6f}")
    report_lines.append(f"Macro precision: {metrics['precision']:.6f}")
    report_lines.append(f"Macro recall: {metrics['recall']:.6f}")
    report_lines.append(f"Macro F1: {metrics['f1']:.6f}")
else:
    report_lines.append("Metrics unavailable.")
report_lines.append("")

report_lines.append("DECISION ENGINE RESULTS")
report_lines.append("-" * 70)
report_lines.append(f"Decision Engine accuracy: {final_accuracy}")
report_lines.append(f"Correct final decisions: {correct_final_decisions}")
report_lines.append(f"Wrong final decisions: {wrong_final_decisions}")
report_lines.append(f"Low-confidence claims: {low_confidence_count}")
report_lines.append("")

report_lines.append("IMPORTANT LIMITATIONS")
report_lines.append("-" * 70)
if gtm_errors:
    report_lines.append("GTM limitations:")
    for error in gtm_errors:
        report_lines.append(f"- {error}")
else:
    report_lines.append("GTM metrics were calculated from the discovered files.")
report_lines.append(
    "Individual Python test metrics are only reported for the selected model "
    "when they exist in model_info.csv."
)
report_lines.append(
    "This report summarizes existing outputs; it does not retrain or recreate GTM."
)
report_lines.append(
    "No claim is made that GTM is better or worse than the Python ML models."
)

REPORT_OUTPUT.write_text(
    "\n".join(report_lines) + "\n",
    encoding="utf-8"
)

print("Created:")
print(COMPARISON_OUTPUT)
print(REPORT_OUTPUT)

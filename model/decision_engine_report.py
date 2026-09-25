from pathlib import Path

import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

AUDIT_FILE = (
    PROJECT_ROOT
    / "model"
    / "decision_engine_audit.csv"
)

RESULT_FILE = (
    PROJECT_ROOT
    / "model"
    / "decision_engine_test_results.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "model"
    / "decision_engine_summary.csv"
)


# =========================================================
# LOAD DATA
# =========================================================

# The audit file is the required summary input.
audit_df = pd.read_csv(AUDIT_FILE)

# Claim-level results are needed for ML accuracy and confusion matrix.
result_df = pd.read_csv(RESULT_FILE)

required_columns = [
    "MLPrediction",
    "FinalDecision",
    "RuleTriggered",
    "DecisionReasons",
    "ActualClass",
]

missing_columns = [
    column
    for column in required_columns
    if column not in result_df.columns
]

if missing_columns:
    raise ValueError(
        "Missing columns in decision_engine_test_results.csv: "
        + ", ".join(missing_columns)
    )


# =========================================================
# BASIC METRICS
# =========================================================

total_claims = len(result_df)

correct_final_decisions = (
    result_df["FinalDecision"]
    == result_df["ActualClass"]
).sum()

wrong_final_decisions = total_claims - correct_final_decisions

final_decision_accuracy = (
    correct_final_decisions / total_claims
    if total_claims
    else 0
)

ml_correct = (
    result_df["MLPrediction"]
    == result_df["ActualClass"]
).sum()

ml_prediction_accuracy = (
    ml_correct / total_claims
    if total_claims
    else 0
)

rule_triggered_claims = (
    result_df["RuleTriggered"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("yes")
    .sum()
)

low_confidence_claims = (
    pd.to_numeric(
        result_df["MLConfidence"],
        errors="coerce"
    )
    < 0.60
).sum()


summary_rows = []


def add_summary(metric, category, value):
    summary_rows.append(
        {
            "Metric": metric,
            "Category": category,
            "Value": value,
        }
    )


add_summary("Basic Metric", "Total claims", total_claims)
add_summary(
    "Basic Metric",
    "Correct final decisions",
    correct_final_decisions
)
add_summary(
    "Basic Metric",
    "Wrong final decisions",
    wrong_final_decisions
)
add_summary(
    "Basic Metric",
    "Final decision accuracy",
    final_decision_accuracy
)
add_summary(
    "Basic Metric",
    "ML prediction accuracy",
    ml_prediction_accuracy
)
add_summary(
    "Basic Metric",
    "Rule-triggered claims",
    rule_triggered_claims
)
add_summary(
    "Basic Metric",
    "Low-confidence claims",
    low_confidence_claims
)


# =========================================================
# CONFUSION MATRIX
# =========================================================

confusion_matrix = pd.crosstab(
    result_df["ActualClass"],
    result_df["FinalDecision"]
)

for actual_class in confusion_matrix.index:
    for final_decision in confusion_matrix.columns:
        add_summary(
            "Confusion Matrix",
            f"Actual={actual_class}; Final={final_decision}",
            confusion_matrix.loc[actual_class, final_decision]
        )


# =========================================================
# WRONG DECISIONS BY REASON
# =========================================================

wrong_df = result_df[
    result_df["FinalDecision"]
    != result_df["ActualClass"]
]

reason_counts = {}

for reasons in wrong_df["DecisionReasons"].fillna(""):
    for reason in str(reasons).split(";"):
        reason = reason.strip()

        if reason:
            reason_counts[reason] = (
                reason_counts.get(reason, 0) + 1
            )

for reason, count in sorted(reason_counts.items()):
    add_summary(
        "Wrong Decision Reason",
        reason,
        count
    )


# Reading the audit file above is intentional. Keep a simple check so the
# report makes it clear when the latest audit has no final accuracy row.
if not (
    (audit_df["Metric"] == "FinalAccuracy").any()
):
    print("Warning: audit file has no FinalAccuracy row.")


summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("Decision engine summary created:")
print(OUTPUT_FILE)

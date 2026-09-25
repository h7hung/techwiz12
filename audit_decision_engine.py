from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_ROOT
    / "model"
    / "decision_engine_test_results.csv"
)


print("=" * 70)
print("ASSUREX - DECISION ENGINE AUDIT")
print("=" * 70)


# =========================================================
# 1. LOAD DATA
# =========================================================

df = pd.read_csv(INPUT_FILE)

print("\n[1] Dataset")
print("-" * 70)

print("Total rows:", len(df))


# =========================================================
# 2. CHECK REQUIRED COLUMNS
# =========================================================

required_columns = [
    "ClaimID",
    "MLPrediction",
    "MLConfidence",
    "FinalDecision",
    "RuleTriggered",
    "DecisionReasons",
    "ActualClass"
]


print("\n[2] Required columns")
print("-" * 70)


missing_columns = []

for column in required_columns:

    if column in df.columns:

        print("[PASS]", column)

    else:

        print("[FAIL]", column)

        missing_columns.append(column)


if missing_columns:

    print("\nMissing columns:")

    for column in missing_columns:
        print("-", column)

    raise SystemExit(
        "Audit stopped because required columns are missing."
    )


# =========================================================
# 3. CHECK CLAIM ID
# =========================================================

print("\n[3] ClaimID check")
print("-" * 70)

duplicate_ids = df[
    df["ClaimID"].duplicated(
        keep=False
    )
]

if len(duplicate_ids) == 0:

    print("[PASS] No duplicate ClaimID")

else:

    print(
        "[FAIL] Duplicate ClaimID:",
        len(duplicate_ids)
    )

    print(
        duplicate_ids[
            ["ClaimID"]
        ].head(20)
    )


# =========================================================
# 4. FINAL DECISION DISTRIBUTION
# =========================================================

print("\n[4] Final Decision distribution")
print("-" * 70)

final_counts = (
    df["FinalDecision"]
    .value_counts()
)

print(final_counts)


# =========================================================
# 5. ACTUAL CLASS DISTRIBUTION
# =========================================================

print("\n[5] Actual Class distribution")
print("-" * 70)

actual_counts = (
    df["ActualClass"]
    .value_counts()
)

print(actual_counts)


# =========================================================
# 6. ML PREDICTION DISTRIBUTION
# =========================================================

print("\n[6] Python ML Prediction distribution")
print("-" * 70)

ml_counts = (
    df["MLPrediction"]
    .value_counts()
)

print(ml_counts)


# =========================================================
# 7. RULE TRIGGER DISTRIBUTION
# =========================================================

print("\n[7] Rule Triggered")
print("-" * 70)

rule_counts = (
    df["RuleTriggered"]
    .value_counts()
)

print(rule_counts)


# =========================================================
# 8. FINAL DECISION VS ACTUAL CLASS
# =========================================================

print("\n[8] Final Decision vs Actual Class")
print("-" * 70)

comparison = pd.crosstab(
    df["ActualClass"],
    df["FinalDecision"]
)

print(comparison)


# =========================================================
# 9. FINAL DECISION CORRECTNESS
# =========================================================

df["FinalCorrect"] = (
    df["ActualClass"]
    ==
    df["FinalDecision"]
)


correct_count = (
    df["FinalCorrect"]
    .sum()
)

total_count = len(df)

accuracy = (
    correct_count /
    total_count
    if total_count > 0
    else 0
)


print("\n[9] Final Decision Accuracy")
print("-" * 70)

print(
    "Correct:",
    correct_count
)

print(
    "Total:",
    total_count
)

print(
    "Accuracy:",
    f"{accuracy * 100:.2f}%"
)


# =========================================================
# 10. WRONG FINAL DECISIONS
# =========================================================

print("\n[10] Wrong Final Decisions")
print("-" * 70)

wrong = df[
    df["FinalCorrect"] == False
]


print(
    "Wrong decisions:",
    len(wrong)
)


if len(wrong) > 0:

    print("\nFirst 20 wrong decisions:")

    print(
        wrong[
            [
                "ClaimID",
                "MLPrediction",
                "MLConfidence",
                "FinalDecision",
                "DecisionReasons",
                "ActualClass"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


# =========================================================
# 11. RULE REASONS
# =========================================================

print("\n[11] Decision Reasons")
print("-" * 70)


reason_series = (
    df["DecisionReasons"]
    .fillna("")
    .astype(str)
)


reason_counts = {}


for text in reason_series:

    if not text.strip():
        continue

    reasons = [
        x.strip()
        for x in text.split(";")
        if x.strip()
    ]

    for reason in reasons:

        reason_counts[reason] = (
            reason_counts.get(
                reason,
                0
            ) + 1
        )


for reason, count in sorted(
    reason_counts.items(),
    key=lambda x: x[1],
    reverse=True
):

    print(
        f"{reason}: {count}"
    )


# =========================================================
# 12. LOW CONFIDENCE
# =========================================================

print("\n[12] Low confidence claims")
print("-" * 70)

low_confidence = df[
    pd.to_numeric(
        df["MLConfidence"],
        errors="coerce"
    ) < 0.60
]


print(
    "Low confidence:",
    len(low_confidence)
)


if len(low_confidence) > 0:

    print(
        low_confidence[
            [
                "ClaimID",
                "MLPrediction",
                "MLConfidence",
                "FinalDecision",
                "DecisionReasons",
                "ActualClass"
            ]
        ]
        .to_string(index=False)
    )


# =========================================================
# 13. SAVE AUDIT REPORT
# =========================================================

output_file = (
    PROJECT_ROOT
    / "model"
    / "decision_engine_audit.csv"
)


summary = []


for decision, count in final_counts.items():

    summary.append({

        "Metric":
            "FinalDecision",

        "Category":
            decision,

        "Count":
            count

    })


for reason, count in reason_counts.items():

    summary.append({

        "Metric":
            "DecisionReason",

        "Category":
            reason,

        "Count":
            count

    })


summary.append({

    "Metric":
        "FinalAccuracy",

    "Category":
        "All Test Claims",

    "Count":
        accuracy

})


audit_df = pd.DataFrame(
    summary
)


audit_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


print("\n[13] Audit report")
print("-" * 70)

print(
    "Saved:",
    output_file
)


print("\n" + "=" * 70)
print("AUDIT COMPLETED")
print("=" * 70)
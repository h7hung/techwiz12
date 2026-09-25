import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 70)
print("ASSUREX CLAIM ENGINE")
print("DATA LEAKAGE AUDIT")
print("=" * 70)

# ============================================================
# PATH
# ============================================================

DATA_PATH = Path("data/processed/train_processed.csv")

df = pd.read_csv(DATA_PATH)

TARGET = "ClaimClass"

print("\nDataset shape:")
print(df.shape)

print("\nTarget distribution:")
print(df[TARGET].value_counts())


# ============================================================
# 1. FEATURE vs TARGET DISTRIBUTION
# ============================================================

print("\n")
print("=" * 70)
print("1. CATEGORICAL FEATURE DISTRIBUTION")
print("=" * 70)

categorical_columns = df.select_dtypes(
    include=["object", "category", "bool"]
).columns.tolist()

categorical_columns = [
    col for col in categorical_columns
    if col != TARGET
]

for col in categorical_columns:

    print("\n" + "-" * 60)
    print(f"Feature: {col}")

    table = pd.crosstab(
        df[col],
        df[TARGET],
        normalize="index"
    )

    print(table.round(3))


# ============================================================
# 2. NUMERICAL FEATURES BY CLASS
# ============================================================

print("\n")
print("=" * 70)
print("2. NUMERICAL FEATURES BY CLASS")
print("=" * 70)

numeric_columns = df.select_dtypes(
    include=["int64", "float64", "int32", "float32"]
).columns.tolist()

numeric_columns = [
    col for col in numeric_columns
    if col != TARGET
]

summary = df.groupby(TARGET)[numeric_columns].mean().T

print(summary.round(3))


# ============================================================
# 3. UNIQUE / NEAR UNIQUE FEATURES
# ============================================================

print("\n")
print("=" * 70)
print("3. UNIQUE VALUE CHECK")
print("=" * 70)

for col in df.columns:

    if col == TARGET:
        continue

    unique_count = df[col].nunique()
    ratio = unique_count / len(df)

    if ratio > 0.8:

        print(
            f"{col:35s} "
            f"unique={unique_count:5d} "
            f"ratio={ratio:.3f}"
        )


# ============================================================
# 4. PERFECT TARGET SEPARATION
# ============================================================

print("\n")
print("=" * 70)
print("4. POSSIBLE PERFECT SEPARATION")
print("=" * 70)

suspicious_features = []

for col in df.columns:

    if col == TARGET:
        continue

    try:

        grouped = df.groupby(col)[TARGET].nunique()

        max_classes = grouped.max()

        if max_classes == 1:

            suspicious_features.append(col)

            print(
                f"[WARNING] {col} "
                f"can perfectly separate some target groups."
            )

    except Exception:
        pass


# ============================================================
# 5. CLASS CONDITIONAL PROBABILITY
# ============================================================

print("\n")
print("=" * 70)
print("5. STRONG TARGET CORRELATION CHECK")
print("=" * 70)

for col in categorical_columns:

    print(f"\nFeature: {col}")

    ctab = pd.crosstab(
        df[col],
        df[TARGET],
        normalize="index"
    )

    for value, row in ctab.iterrows():

        max_probability = row.max()

        if max_probability >= 0.95:

            predicted_class = row.idxmax()

            print(
                f"  {value} -> "
                f"{predicted_class} "
                f"({max_probability:.3f})"
            )


# ============================================================
# 6. SAVE REPORT
# ============================================================

report_rows = []

for col in df.columns:

    if col == TARGET:
        continue

    row = {
        "Feature": col,
        "UniqueValues": df[col].nunique(),
        "MissingValues": df[col].isna().sum()
    }

    if df[col].dtype == "object":

        ctab = pd.crosstab(
            df[col],
            df[TARGET],
            normalize="index"
        )

        if len(ctab) > 0:

            max_class_probability = ctab.max(axis=1).max()

            row[
                "MaxClassConditionalProbability"
            ] = max_class_probability

        else:

            row[
                "MaxClassConditionalProbability"
            ] = np.nan

    else:

        row[
            "MaxClassConditionalProbability"
        ] = np.nan

    report_rows.append(row)


report = pd.DataFrame(report_rows)

output_path = Path("model/leakage_audit.csv")

report.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# FINAL
# ============================================================

print("\n")
print("=" * 70)
print("LEAKAGE AUDIT COMPLETED")
print("=" * 70)

print(f"\nSaved:")
print(output_path)

print("\nSuspicious features:")

if suspicious_features:

    for feature in suspicious_features:
        print(f" - {feature}")

else:

    print("None detected by this basic audit.")

print("\nNext step:")
print("Review the suspicious features before finalizing the model.")
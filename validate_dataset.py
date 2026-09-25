import pandas as pd
from pathlib import Path


# ============================================================
# ASSUREX CLAIM ENGINE
# DATASET VALIDATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "assurex_common_dataset.csv"
)


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 60)
print("ASSUREX CLAIM ENGINE")
print("COMMON DATASET VALIDATION")
print("=" * 60)

print("\nLoading dataset...")

df = pd.read_csv(
    DATASET_PATH
)

print(
    f"Dataset loaded successfully: {len(df)} records"
)


# ============================================================
# 1. BASIC INFORMATION
# ============================================================

print("\n")
print("=" * 60)
print("1. BASIC INFORMATION")
print("=" * 60)

print(
    f"Rows    : {df.shape[0]}"
)

print(
    f"Columns : {df.shape[1]}"
)

print("\nColumns:")

for index, column in enumerate(
    df.columns,
    start=1
):

    print(
        f"{index:02d}. {column}"
    )


# ============================================================
# 2. CLASS DISTRIBUTION
# ============================================================

print("\n")
print("=" * 60)
print("2. CLASS DISTRIBUTION")
print("=" * 60)

class_counts = (
    df["ClaimClass"]
    .value_counts()
)

print(
    class_counts
)


expected_classes = {
    "Valid Claim": 500,
    "Invalid Claim": 500,
    "Manual Review": 500
}


for class_name, expected_count in (
    expected_classes.items()
):

    actual_count = int(
        class_counts.get(
            class_name,
            0
        )
    )

    if actual_count == expected_count:

        print(
            f"PASS - {class_name}: "
            f"{actual_count}"
        )

    else:

        print(
            f"FAIL - {class_name}: "
            f"Expected {expected_count}, "
            f"got {actual_count}"
        )


# ============================================================
# 3. DUPLICATE CLAIM ID
# ============================================================

print("\n")
print("=" * 60)
print("3. DUPLICATE CLAIM ID")
print("=" * 60)

duplicate_claim_ids = (
    df["ClaimID"]
    .duplicated()
    .sum()
)

print(
    f"Duplicate Claim IDs: "
    f"{duplicate_claim_ids}"
)

if duplicate_claim_ids == 0:

    print(
        "PASS - All Claim IDs are unique"
    )

else:

    print(
        "FAIL - Duplicate Claim IDs detected"
    )


# ============================================================
# 4. MISSING VALUES
# ============================================================

print("\n")
print("=" * 60)
print("4. MISSING VALUES")
print("=" * 60)

missing_values = (
    df.isnull()
    .sum()
)

missing_values = (
    missing_values[
        missing_values > 0
    ]
)

if len(missing_values) == 0:

    print(
        "PASS - No missing values"
    )

else:

    print(
        "Columns containing missing values:"
    )

    print(
        missing_values
    )


# ============================================================
# 5. DATE VALIDATION
# ============================================================

print("\n")
print("=" * 60)
print("5. DATE VALIDATION")
print("=" * 60)

date_columns = [
    "PurchaseDate",
    "ClaimDate",
    "FaultDate",
    "WarrantyExpiryDate"
]

for column in date_columns:

    df[column] = pd.to_datetime(
        df[column],
        errors="coerce"
    )

    invalid_dates = (
        df[column]
        .isna()
        .sum()
    )

    if invalid_dates == 0:

        print(
            f"PASS - {column}"
        )

    else:

        print(
            f"FAIL - {column}: "
            f"{invalid_dates} invalid dates"
        )


# ============================================================
# 6. DATE LOGIC
# ============================================================

print("\n")
print("=" * 60)
print("6. DATE LOGIC")
print("=" * 60)

fault_before_purchase = (
    df["FaultDate"]
    < df["PurchaseDate"]
)

claim_before_purchase = (
    df["ClaimDate"]
    < df["PurchaseDate"]
)

fault_after_claim = (
    df["FaultDate"]
    > df["ClaimDate"]
)

print(
    "Fault before purchase:",
    int(fault_before_purchase.sum())
)

print(
    "Claim before purchase:",
    int(claim_before_purchase.sum())
)

print(
    "Fault after claim:",
    int(fault_after_claim.sum())
)


# ============================================================
# 7. WARRANTY STATUS
# ============================================================

print("\n")
print("=" * 60)
print("7. WARRANTY STATUS")
print("=" * 60)

print(
    df["WarrantyStatus"]
    .value_counts()
)


# ============================================================
# 8. SERIAL NUMBER CHECK
# ============================================================

print("\n")
print("=" * 60)
print("8. SERIAL NUMBER")
print("=" * 60)

empty_serials = (
    df["SerialNumber"]
    .isna()
    .sum()
)

duplicate_serials = (
    df["SerialNumber"]
    .duplicated()
    .sum()
)

print(
    f"Empty Serial Numbers : {empty_serials}"
)

print(
    f"Duplicate Serial Numbers : "
    f"{duplicate_serials}"
)


# ============================================================
# 9. DOCUMENT COMPLETENESS
# ============================================================

print("\n")
print("=" * 60)
print("9. DOCUMENT COMPLETENESS")
print("=" * 60)

print(
    df["RequiredDocumentsComplete"]
    .value_counts()
)


# ============================================================
# 10. CONTRADICTION
# ============================================================

print("\n")
print("=" * 60)
print("10. CONTRADICTION")
print("=" * 60)

print(
    df["ContradictionIndicator"]
    .value_counts()
)


# ============================================================
# 11. DUPLICATE CLAIM
# ============================================================

print("\n")
print("=" * 60)
print("11. DUPLICATE CLAIM")
print("=" * 60)

print(
    df["DuplicateClaimIndicator"]
    .value_counts()
)


# ============================================================
# 12. SERIAL MATCH
# ============================================================

print("\n")
print("=" * 60)
print("12. SERIAL MATCH")
print("=" * 60)

print(
    df["SerialNumberMatch"]
    .value_counts()
)


# ============================================================
# 13. REPAIR AUTHORIZATION
# ============================================================

print("\n")
print("=" * 60)
print("13. REPAIR AUTHORIZATION")
print("=" * 60)

print(
    df["RepairAuthorized"]
    .value_counts()
)


# ============================================================
# 14. INVALID CLAIM REASONS
# ============================================================

print("\n")
print("=" * 60)
print("14. INVALID CLAIM ANALYSIS")
print("=" * 60)

invalid_df = df[
    df["ClaimClass"]
    == "Invalid Claim"
]

print(
    "Expired warranty:",
    int(
        (
            invalid_df["WarrantyStatus"]
            == "Expired"
        ).sum()
    )
)

print(
    "Excluded fault:",
    int(
        (
            invalid_df["FaultCovered"]
            == "No"
        ).sum()
    )
)

print(
    "Serial mismatch:",
    int(
        (
            invalid_df["SerialNumberMatch"]
            == "No"
        ).sum()
    )
)

print(
    "Unauthorized repair:",
    int(
        (
            invalid_df["RepairAuthorized"]
            == "No"
        ).sum()
    )
)

print(
    "Reporting period exceeded:",
    int(
        (
            invalid_df[
                "ClaimReportingWithinPeriod"
            ]
            == "No"
        ).sum()
    )
)

print(
    "Duplicate claim:",
    int(
        (
            invalid_df[
                "DuplicateClaimIndicator"
            ]
            == "Yes"
        ).sum()
    )
)


# ============================================================
# 15. MANUAL REVIEW ANALYSIS
# ============================================================

print("\n")
print("=" * 60)
print("15. MANUAL REVIEW ANALYSIS")
print("=" * 60)

manual_df = df[
    df["ClaimClass"]
    == "Manual Review"
]

print(
    "Missing documents:",
    int(
        (
            manual_df[
                "RequiredDocumentsComplete"
            ]
            == "No"
        ).sum()
    )
)

print(
    "Contradictions:",
    int(
        (
            manual_df[
                "ContradictionIndicator"
            ]
            == "Yes"
        ).sum()
    )
)

print(
    "Low OCR confidence:",
    int(
        (
            manual_df[
                "OCRConfidence"
            ]
            < 0.70
        ).sum()
    )
)

print(
    "Unknown serial:",
    int(
        (
            manual_df[
                "SerialNumberMatch"
            ]
            == "Unknown"
        ).sum()
    )
)

print(
    "Unknown repair:",
    int(
        (
            manual_df[
                "RepairAuthorized"
            ]
            == "Unknown"
        ).sum()
    )
)


# ============================================================
# 16. DATA SAMPLE
# ============================================================

print("\n")
print("=" * 60)
print("16. FIRST 5 RECORDS")
print("=" * 60)

print(
    df.head(5).to_string(
        index=False
    )
)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 60)
print("DATASET VALIDATION FINISHED")
print("=" * 60)
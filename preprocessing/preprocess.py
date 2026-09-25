import pandas as pd
import numpy as np

from pathlib import Path


# ============================================================
# ASSUREX CLAIM ENGINE
# PREPROCESSING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_PATH = (
    BASE_DIR
    / "data"
    / "train"
    / "assurex_train.csv"
)

VALIDATION_PATH = (
    BASE_DIR
    / "data"
    / "validation"
    / "assurex_validation.csv"
)

TEST_PATH = (
    BASE_DIR
    / "data"
    / "test"
    / "assurex_test.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("ASSUREX CLAIM ENGINE")
print("PYTHON ML PREPROCESSING")
print("=" * 60)

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
# FEATURE ENGINEERING
# ============================================================

DATE_COLUMNS = [
    "PurchaseDate",
    "ClaimDate",
    "FaultDate",
    "WarrantyExpiryDate"
]


def create_features(df):

    df = df.copy()

    # --------------------------------------------------------
    # Convert dates
    # --------------------------------------------------------

    for column in DATE_COLUMNS:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Product age
    # --------------------------------------------------------

    df["ProductAgeDays"] = (
        df["ClaimDate"]
        - df["PurchaseDate"]
    ).dt.days

    # --------------------------------------------------------
    # Warranty remaining
    # --------------------------------------------------------

    df["WarrantyRemainingDays"] = (
        df["WarrantyExpiryDate"]
        - df["ClaimDate"]
    ).dt.days

    # --------------------------------------------------------
    # Missing document count
    # --------------------------------------------------------

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
            lambda row:
            sum(
                value == "No"
                for value in row
            ),
            axis=1
        )
    )

    # --------------------------------------------------------
    # Claim reporting delay
    # --------------------------------------------------------

    df["ClaimReportingDelayDays"] = (
        df["ClaimDate"]
        - df["FaultDate"]
    ).dt.days

    # --------------------------------------------------------
    # Repair indicator
    # --------------------------------------------------------

    df["HasRepairHistory"] = (
        df["PreviousRepair"]
        .map(
            {
                "Yes": 1,
                "No": 0
            }
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # Previous replacement indicator
    # --------------------------------------------------------

    df["HasPreviousReplacement"] = (
        df["PreviousReplacement"]
        .map(
            {
                "Yes": 1,
                "No": 0
            }
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # Remove raw date columns
    # --------------------------------------------------------

    df = df.drop(
        columns=DATE_COLUMNS
    )

    return df


# ============================================================
# APPLY FEATURE ENGINEERING
# ============================================================

train_processed = create_features(
    train_df
)

validation_processed = create_features(
    validation_df
)

test_processed = create_features(
    test_df
)


# ============================================================
# REMOVE IDENTIFIERS / METADATA
# ============================================================

DROP_COLUMNS = [
    "ClaimID",
    "ScenarioID",
    "CustomerID",
    "ProductID",
    "SerialNumber"
]


def prepare_xy(df):

    df = df.copy()

    # Target
    y = df["ClaimClass"]

    # Remove target
    X = df.drop(
        columns=["ClaimClass"]
    )

    # Remove identifiers
    X = X.drop(
        columns=DROP_COLUMNS,
        errors="ignore"
    )

    return X, y


X_train, y_train = prepare_xy(
    train_processed
)

X_validation, y_validation = prepare_xy(
    validation_processed
)

X_test, y_test = prepare_xy(
    test_processed
)


# ============================================================
# DISPLAY FEATURE INFORMATION
# ============================================================

print("\n")
print("=" * 60)
print("FEATURE INFORMATION")
print("=" * 60)

print(
    f"Number of features: {X_train.shape[1]}"
)

print("\nFeatures:")

for index, column in enumerate(
    X_train.columns,
    start=1
):

    print(
        f"{index:02d}. {column}"
    )


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

print("\n")
print("=" * 60)
print("TARGET DISTRIBUTION")
print("=" * 60)

print(
    y_train.value_counts()
)

print("\nValidation:")

print(
    y_validation.value_counts()
)

print("\nTest:")

print(
    y_test.value_counts()
)


# ============================================================
# SAVE PROCESSED DATA
# ============================================================

PROCESSED_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


train_processed.to_csv(
    PROCESSED_DIR
    / "train_processed.csv",
    index=False,
    encoding="utf-8-sig"
)

validation_processed.to_csv(
    PROCESSED_DIR
    / "validation_processed.csv",
    index=False,
    encoding="utf-8-sig"
)

test_processed.to_csv(
    PROCESSED_DIR
    / "test_processed.csv",
    index=False,
    encoding="utf-8-sig"
)


print("\n")
print("=" * 60)
print("PREPROCESSING COMPLETED")
print("=" * 60)

print(
    "Processed files saved to:"
)

print(
    PROCESSED_DIR
)

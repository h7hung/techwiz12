import pandas as pd
from pathlib import Path


print("=" * 60)
print("ASSUREX CLAIM ENGINE")
print("GTM DATASET CHECK")
print("=" * 60)


# ============================================================
# FILES
# ============================================================

TRAIN_CSV = Path(
    "data/train/assurex_train.csv"
)

VALIDATION_CSV = Path(
    "data/validation/assurex_validation.csv"
)

TEST_CSV = Path(
    "data/test/assurex_test.csv"
)


# ============================================================
# READ DATA
# ============================================================

train = pd.read_csv(TRAIN_CSV)
validation = pd.read_csv(VALIDATION_CSV)
test = pd.read_csv(TEST_CSV)


# ============================================================
# BASIC INFORMATION
# ============================================================

print("\nDataset size:")

print(
    "Train      :",
    len(train)
)

print(
    "Validation :",
    len(validation)
)

print(
    "Test       :",
    len(test)
)


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

print("\n")
print("=" * 60)
print("CLASS DISTRIBUTION")
print("=" * 60)


print("\nTRAIN")

print(
    train["ClaimClass"].value_counts()
)


print("\nVALIDATION")

print(
    validation["ClaimClass"].value_counts()
)


print("\nTEST")

print(
    test["ClaimClass"].value_counts()
)


# ============================================================
# CLAIM ID
# ============================================================

print("\n")
print("=" * 60)
print("CLAIM ID CHECK")
print("=" * 60)


train_ids = set(
    train["ClaimID"].astype(str)
)

validation_ids = set(
    validation["ClaimID"].astype(str)
)

test_ids = set(
    test["ClaimID"].astype(str)
)


print(
    "Train IDs      :",
    len(train_ids)
)

print(
    "Validation IDs :",
    len(validation_ids)
)

print(
    "Test IDs       :",
    len(test_ids)
)


# ============================================================
# OVERLAP CHECK
# ============================================================

print("\n")
print("=" * 60)
print("OVERLAP CHECK")
print("=" * 60)


train_validation = (
    train_ids & validation_ids
)

train_test = (
    train_ids & test_ids
)

validation_test = (
    validation_ids & test_ids
)


if len(train_validation) == 0:

    print(
        "✓ Train / Validation: NO OVERLAP"
    )

else:

    print(
        "✗ Train / Validation: OVERLAP"
    )


if len(train_test) == 0:

    print(
        "✓ Train / Test: NO OVERLAP"
    )

else:

    print(
        "✗ Train / Test: OVERLAP"
    )


if len(validation_test) == 0:

    print(
        "✓ Validation / Test: NO OVERLAP"
    )

else:

    print(
        "✗ Validation / Test: OVERLAP"
    )


# ============================================================
# FINAL
# ============================================================

print("\n")
print("=" * 60)
print("GTM DATASET CHECK COMPLETED")
print("=" * 60)
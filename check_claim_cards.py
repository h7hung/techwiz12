import pandas as pd
from pathlib import Path


print("=" * 60)
print("ASSUREX CLAIM SUMMARY CARD CHECK")
print("=" * 60)


# ============================================================
# 1. ĐƯỜNG DẪN
# ============================================================

TRAIN_CSV = Path("data/train/assurex_train.csv")
VALIDATION_CSV = Path("data/validation/assurex_validation.csv")
TEST_CSV = Path("data/test/assurex_test.csv")

TRAIN_FOLDER = Path("claim_cards/train")
VALIDATION_FOLDER = Path("claim_cards/validation")
TEST_FOLDER = Path("claim_cards/test")


# ============================================================
# 2. ĐỌC CSV
# ============================================================

train = pd.read_csv(TRAIN_CSV)
validation = pd.read_csv(VALIDATION_CSV)
test = pd.read_csv(TEST_CSV)


print("\nDataset:")

print("Train      :", len(train))
print("Validation :", len(validation))
print("Test       :", len(test))


# ============================================================
# 3. ĐẾM ẢNH
# ============================================================

train_v1 = list(
    (TRAIN_FOLDER / "variation_01").glob("*.png")
)

train_v2 = list(
    (TRAIN_FOLDER / "variation_02").glob("*.png")
)

validation_images = list(
    (VALIDATION_FOLDER / "variation_01").glob("*.png")
)

test_images = list(
    (TEST_FOLDER / "variation_01").glob("*.png")
)


print("\nImages:")

print(
    "Train variation 01 :",
    len(train_v1)
)

print(
    "Train variation 02 :",
    len(train_v2)
)

print(
    "Validation         :",
    len(validation_images)
)

print(
    "Test               :",
    len(test_images)
)


# ============================================================
# 4. KIỂM TRA SỐ LƯỢNG
# ============================================================

print("\n")
print("=" * 60)
print("COUNT CHECK")
print("=" * 60)


if len(train_v1) == 1050:
    print("✓ Train variation 01: OK")
else:
    print("✗ Train variation 01: SAI")


if len(train_v2) == 1050:
    print("✓ Train variation 02: OK")
else:
    print("✗ Train variation 02: SAI")


if len(validation_images) == 225:
    print("✓ Validation: OK")
else:
    print("✗ Validation: SAI")


if len(test_images) == 225:
    print("✓ Test: OK")
else:
    print("✗ Test: SAI")


# ============================================================
# 5. KIỂM TRA CLAIM ID
# ============================================================

print("\n")
print("=" * 60)
print("CLAIM ID CHECK")
print("=" * 60)


def get_claim_ids(image_list):

    claim_ids = []

    for image in image_list:

        # Ví dụ:
        # SN-2026-000001_v01.png
        # → SN-2026-000001

        name = image.stem

        claim_id = name.rsplit("_v", 1)[0]

        claim_ids.append(claim_id)

    return set(claim_ids)


train_ids = set(
    train["ClaimID"].astype(str)
)

validation_ids = set(
    validation["ClaimID"].astype(str)
)

test_ids = set(
    test["ClaimID"].astype(str)
)


train_card_ids = get_claim_ids(
    train_v1
)

validation_card_ids = get_claim_ids(
    validation_images
)

test_card_ids = get_claim_ids(
    test_images
)


# ============================================================
# TRAIN
# ============================================================

missing_train = (
    train_ids - train_card_ids
)

extra_train = (
    train_card_ids - train_ids
)


if not missing_train and not extra_train:

    print(
        "✓ Train ClaimID: KHỚP"
    )

else:

    print(
        "✗ Train ClaimID: SAI"
    )

    print(
        "Missing:",
        missing_train
    )

    print(
        "Extra:",
        extra_train
    )


# ============================================================
# VALIDATION
# ============================================================

missing_validation = (
    validation_ids - validation_card_ids
)

extra_validation = (
    validation_card_ids - validation_ids
)


if not missing_validation and not extra_validation:

    print(
        "✓ Validation ClaimID: KHỚP"
    )

else:

    print(
        "✗ Validation ClaimID: SAI"
    )

    print(
        "Missing:",
        missing_validation
    )

    print(
        "Extra:",
        extra_validation
    )


# ============================================================
# TEST
# ============================================================

missing_test = (
    test_ids - test_card_ids
)

extra_test = (
    test_card_ids - test_ids
)


if not missing_test and not extra_test:

    print(
        "✓ Test ClaimID: KHỚP"
    )

else:

    print(
        "✗ Test ClaimID: SAI"
    )

    print(
        "Missing:",
        missing_test
    )

    print(
        "Extra:",
        extra_test
    )


# ============================================================
# 6. KIỂM TRA TRAIN KHÔNG TRÙNG VALIDATION / TEST
# ============================================================

print("\n")
print("=" * 60)
print("DATA SPLIT CHECK")
print("=" * 60)


train_validation_overlap = (
    train_ids & validation_ids
)

train_test_overlap = (
    train_ids & test_ids
)

validation_test_overlap = (
    validation_ids & test_ids
)


if not train_validation_overlap:

    print(
        "✓ Train / Validation: KHÔNG TRÙNG"
    )

else:

    print(
        "✗ Train / Validation: CÓ TRÙNG"
    )


if not train_test_overlap:

    print(
        "✓ Train / Test: KHÔNG TRÙNG"
    )

else:

    print(
        "✗ Train / Test: CÓ TRÙNG"
    )


if not validation_test_overlap:

    print(
        "✓ Validation / Test: KHÔNG TRÙNG"
    )

else:

    print(
        "✗ Validation / Test: CÓ TRÙNG"
    )


# ============================================================
# 7. KẾT QUẢ
# ============================================================

print("\n")
print("=" * 60)
print("CHECK COMPLETED")
print("=" * 60)
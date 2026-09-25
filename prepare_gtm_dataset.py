from pathlib import Path
import pandas as pd
import shutil

# =========================================================
# CONFIG
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

CSV_FILE = PROJECT_ROOT / "data" / "train" / "assurex_train.csv"

SOURCE_V01 = (
    PROJECT_ROOT
    / "claim_cards"
    / "train"
    / "variation_01"
)

SOURCE_V02 = (
    PROJECT_ROOT
    / "claim_cards"
    / "train"
    / "variation_02"
)

OUTPUT_FOLDER = PROJECT_ROOT / "gtm_dataset"

CLASS_NAMES = [
    "Valid Claim",
    "Invalid Claim",
    "Manual Review"
]

# =========================================================
# CREATE FOLDERS
# =========================================================

print("=" * 60)
print("ASSUREX - PREPARE GTM DATASET")
print("=" * 60)

print("\n[1] Creating GTM folders...")

for class_name in CLASS_NAMES:
    folder = OUTPUT_FOLDER / class_name
    folder.mkdir(parents=True, exist_ok=True)
    print("Created:", folder)

# =========================================================
# READ TRAIN CSV
# =========================================================

print("\n[2] Reading training CSV...")

if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"Training CSV not found:\n{CSV_FILE}"
    )

df = pd.read_csv(CSV_FILE)

print("Training claims:", len(df))

required_columns = ["ClaimID", "ClaimClass"]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Missing required column: {column}"
        )

# =========================================================
# COPY IMAGES
# =========================================================

print("\n[3] Copying training images...")

total_copied = 0
total_missing = 0

for index, row in df.iterrows():

    claim_id = str(row["ClaimID"]).strip()
    claim_class = str(row["ClaimClass"]).strip()

    # Check class
    if claim_class not in CLASS_NAMES:
        print(
            f"WARNING: Unknown class for {claim_id}: "
            f"{claim_class}"
        )
        continue

    destination_folder = OUTPUT_FOLDER / claim_class

    # ---------------------------------------------
    # Variation 01
    # ---------------------------------------------

    source_v01 = SOURCE_V01 / f"{claim_id}_v01.png"

    if source_v01.exists():

        destination_v01 = (
            destination_folder
            / f"{claim_id}_v01.png"
        )

        shutil.copy2(
            source_v01,
            destination_v01
        )

        total_copied += 1

    else:

        print(
            f"WARNING: Missing V01 image: "
            f"{source_v01}"
        )

        total_missing += 1

    # ---------------------------------------------
    # Variation 02
    # ---------------------------------------------

    source_v02 = SOURCE_V02 / f"{claim_id}_v02.png"

    if source_v02.exists():

        destination_v02 = (
            destination_folder
            / f"{claim_id}_v02.png"
        )

        shutil.copy2(
            source_v02,
            destination_v02
        )

        total_copied += 1

    else:

        print(
            f"WARNING: Missing V02 image: "
            f"{source_v02}"
        )

        total_missing += 1

    # ---------------------------------------------
    # Progress
    # ---------------------------------------------

    current = index + 1

    if current % 50 == 0 or current == len(df):

        print(
            f"Progress: {current}/{len(df)} "
            f"({current / len(df) * 100:.1f}%)"
        )

# =========================================================
# CHECK RESULT
# =========================================================

print("\n[4] Checking GTM dataset...")

print()

grand_total = 0

for class_name in CLASS_NAMES:

    folder = OUTPUT_FOLDER / class_name

    images = list(folder.glob("*.png"))

    count = len(images)

    grand_total += count

    print(
        f"{class_name}: {count} images"
    )

print()
print("=" * 60)
print("RESULT")
print("=" * 60)

print("Expected images : 2100")
print("Copied images   :", total_copied)
print("Missing images  :", total_missing)
print("Actual images   :", grand_total)

# =========================================================
# FINAL CHECK
# =========================================================

expected_per_class = 700

print("\nClass verification:")

all_pass = True

for class_name in CLASS_NAMES:

    folder = OUTPUT_FOLDER / class_name

    count = len(list(folder.glob("*.png")))

    if count == expected_per_class:

        print(
            f"[PASS] {class_name}: "
            f"{count}/700"
        )

    else:

        print(
            f"[FAIL] {class_name}: "
            f"{count}/700"
        )

        all_pass = False

print()

if grand_total == 2100 and total_missing == 0 and all_pass:

    print("=" * 60)
    print("SUCCESS!")
    print("GTM dataset is ready.")
    print("=" * 60)

else:

    print("=" * 60)
    print("WARNING!")
    print("GTM dataset is NOT complete.")
    print("Please check the missing images.")
    print("=" * 60)
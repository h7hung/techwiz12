from collections import Counter
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent

DATASET_FILES = {
    "Common dataset": PROJECT_ROOT / "data" / "raw" / "assurex_common_dataset.csv",
    "Train dataset": PROJECT_ROOT / "data" / "train" / "assurex_train.csv",
    "Validation dataset": PROJECT_ROOT / "data" / "validation" / "assurex_validation.csv",
    "Test dataset": PROJECT_ROOT / "data" / "test" / "assurex_test.csv",
    "Processed train": PROJECT_ROOT / "data" / "processed" / "train_processed.csv",
    "Processed validation": PROJECT_ROOT / "data" / "processed" / "validation_processed.csv",
    "Processed test": PROJECT_ROOT / "data" / "processed" / "test_processed.csv",
}

MODEL_FILES = {
    "Final Python model": PROJECT_ROOT / "model" / "assurex_final_model.joblib",
    "Model comparison": PROJECT_ROOT / "model" / "model_comparison.csv",
    "Python confusion matrix": PROJECT_ROOT / "model" / "confusion_matrix.csv",
    "Model information": PROJECT_ROOT / "model" / "model_info.csv",
    "Sample predictions": PROJECT_ROOT / "model" / "sample_test_predictions.csv",
}

DECISION_ENGINE_FILES = {
    "Decision engine results": PROJECT_ROOT / "model" / "decision_engine_test_results.csv",
    "Decision engine audit": PROJECT_ROOT / "model" / "decision_engine_audit.csv",
    "Decision engine script": PROJECT_ROOT / "decision_engine.py",
}

GTM_EVALUATION_NAMES = [
    "validation_predictions.csv",
    "validation_confusion_matrix.csv",
    "test_predictions.csv",
    "test_confusion_matrix.csv",
]

EXPECTED_ROWS = {
    "Common dataset": 1500,
    "Train dataset": 1050,
    "Validation dataset": 225,
    "Test dataset": 225,
    "Processed train": 1050,
    "Processed validation": 225,
    "Processed test": 225,
}


results = []


def add_result(status, requirement, actual, notes=""):
    results.append(
        {
            "status": status,
            "requirement": requirement,
            "actual": actual,
            "notes": notes,
        }
    )


def check_file_group(file_group):
    for requirement, path in file_group.items():
        if path.exists() and path.is_file():
            add_result("PASS", requirement, str(path.relative_to(PROJECT_ROOT)))
        else:
            add_result("FAIL", requirement, "Missing", str(path.relative_to(PROJECT_ROOT)))


def load_csv(path):
    if not path.exists():
        return None
    return pd.read_csv(path)


# =========================================================
# REQUIRED FILES
# =========================================================

check_file_group(DATASET_FILES)
check_file_group(MODEL_FILES)
check_file_group(DECISION_ENGINE_FILES)

preprocess_file = PROJECT_ROOT / "preprocessing" / "preprocess.py"
train_file = PROJECT_ROOT / "model" / "train_models.py"

add_result(
    "PASS" if preprocess_file.is_file() else "FAIL",
    "Preprocessing script",
    str(preprocess_file.relative_to(PROJECT_ROOT)) if preprocess_file.is_file() else "Missing",
)
add_result(
    "PASS" if train_file.is_file() else "FAIL",
    "Training script",
    str(train_file.relative_to(PROJECT_ROOT)) if train_file.is_file() else "Missing",
)

claim_cards_dir = PROJECT_ROOT / "claim_cards"
gtm_dataset_dir = PROJECT_ROOT / "gtm_dataset"
gtm_model_dir = PROJECT_ROOT / "model" / "gtm_model"

add_result(
    "PASS" if claim_cards_dir.is_dir() else "FAIL",
    "GTM claim_cards directory",
    "Exists" if claim_cards_dir.is_dir() else "Missing",
)
add_result(
    "PASS" if gtm_dataset_dir.is_dir() else "FAIL",
    "GTM gtm_dataset directory",
    "Exists" if gtm_dataset_dir.is_dir() else "Missing",
)

if gtm_model_dir.is_dir():
    gtm_model_files = [path for path in gtm_model_dir.rglob("*") if path.is_file()]
    add_result("PASS" if gtm_model_files else "FAIL", "GTM model files", len(gtm_model_files))
else:
    add_result("FAIL", "GTM model files", "Missing model directory")

for file_name in GTM_EVALUATION_NAMES:
    matches = list(PROJECT_ROOT.rglob(file_name))
    if matches:
        add_result("PASS", f"GTM evaluation: {file_name}", str(matches[0].relative_to(PROJECT_ROOT)))
    else:
        add_result("FAIL", f"GTM evaluation: {file_name}", "Missing")


# =========================================================
# DATASET CHECKS
# =========================================================

frames = {
    name: load_csv(path)
    for name, path in DATASET_FILES.items()
}

for name, expected_rows in EXPECTED_ROWS.items():
    dataframe = frames[name]
    actual_rows = len(dataframe) if dataframe is not None else 0
    status = "PASS" if actual_rows == expected_rows else "FAIL"
    add_result(status, f"{name} row count", actual_rows, f"Expected {expected_rows}")

common_df = frames["Common dataset"]
if common_df is not None and "ClaimClass" in common_df.columns:
    class_counts = common_df["ClaimClass"].value_counts().to_dict()
    expected_classes = {
        "Valid Claim": 500,
        "Invalid Claim": 500,
        "Manual Review": 500,
    }
    status = "PASS" if class_counts == expected_classes else "FAIL"
    add_result(status, "Common dataset class distribution", class_counts, f"Expected {expected_classes}")
else:
    add_result("FAIL", "Common dataset class distribution", "ClaimClass column unavailable")

split_frames = {
    name: frames[name]
    for name in ["Train dataset", "Validation dataset", "Test dataset"]
}

if all(dataframe is not None and "ClaimID" in dataframe.columns for dataframe in split_frames.values()):
    train_ids = set(split_frames["Train dataset"]["ClaimID"])
    validation_ids = set(split_frames["Validation dataset"]["ClaimID"])
    test_ids = set(split_frames["Test dataset"]["ClaimID"])
    overlap = (
        train_ids & validation_ids
        | train_ids & test_ids
        | validation_ids & test_ids
    )
    add_result("PASS" if not overlap else "FAIL", "ClaimID overlap between splits", len(overlap), "Expected 0")
    add_result(
        "PASS" if not train_ids & validation_ids else "FAIL",
        "Validation ClaimIDs overlap training ClaimIDs",
        len(train_ids & validation_ids),
        "Expected 0",
    )
    add_result(
        "PASS" if not train_ids & test_ids else "FAIL",
        "Test ClaimIDs overlap training ClaimIDs",
        len(train_ids & test_ids),
        "Expected 0",
    )
else:
    add_result("FAIL", "ClaimID overlap between splits", "ClaimID column unavailable")
    add_result("FAIL", "Validation ClaimIDs overlap training ClaimIDs", "ClaimID column unavailable")
    add_result("FAIL", "Test ClaimIDs overlap training ClaimIDs", "ClaimID column unavailable")


# =========================================================
# IMAGE CHECKS
# =========================================================

image_root = PROJECT_ROOT / "claim_cards"
train_images = list((image_root / "train").rglob("*.png")) if image_root.exists() else []
validation_images = list((image_root / "validation").rglob("*.png")) if image_root.exists() else []
test_images = list((image_root / "test").rglob("*.png")) if image_root.exists() else []

add_result("PASS" if len(train_images) == 2100 else "FAIL", "Training image count", len(train_images), "Expected 2100")

train_df = frames["Train dataset"]
if train_df is not None and "ClaimID" in train_df.columns and "ClaimClass" in train_df.columns:
    class_by_claim = train_df.set_index("ClaimID")["ClaimClass"].to_dict()
    images_by_class = Counter()
    images_by_claim = Counter()

    for image_path in train_images:
        claim_id = image_path.stem.rsplit("_v", 1)[0]
        images_by_claim[claim_id] += 1
        if claim_id in class_by_claim:
            images_by_class[class_by_claim[claim_id]] += 1

    expected_image_classes = {
        "Valid Claim": 700,
        "Invalid Claim": 700,
        "Manual Review": 700,
    }
    add_result(
        "PASS" if dict(images_by_class) == expected_image_classes else "FAIL",
        "Training image count per class",
        dict(images_by_class),
        f"Expected {expected_image_classes}",
    )

    expected_claim_count = len(train_df)
    two_variations = (
        len(images_by_claim) == expected_claim_count
        and all(count == 2 for count in images_by_claim.values())
    )
    add_result(
        "PASS" if two_variations else "FAIL",
        "Two image variations per training claim",
        f"{len(images_by_claim)} claims, counts={sorted(set(images_by_claim.values()))}",
        "Expected exactly 2 images for every train ClaimID",
    )
else:
    add_result("FAIL", "Training image count per class", "Train ClaimClass unavailable")
    add_result("FAIL", "Two image variations per training claim", "Train ClaimID unavailable")

add_result("PASS" if len(validation_images) == 225 else "FAIL", "Validation image count", len(validation_images), "Expected 225")
add_result("PASS" if len(test_images) == 225 else "FAIL", "Test image count", len(test_images), "Expected 225")


def image_claim_ids(image_paths):
    return {
        path.stem.rsplit("_v", 1)[0]
        for path in image_paths
    }


if train_df is not None and "ClaimID" in train_df.columns:
    training_claim_ids = set(train_df["ClaimID"])
    validation_overlap = training_claim_ids & image_claim_ids(validation_images)
    test_overlap = training_claim_ids & image_claim_ids(test_images)
    add_result("PASS" if not validation_overlap else "FAIL", "Validation image ClaimIDs overlap training", len(validation_overlap), "Expected 0")
    add_result("PASS" if not test_overlap else "FAIL", "Test image ClaimIDs overlap training", len(test_overlap), "Expected 0")
else:
    add_result("FAIL", "Validation/test ClaimIDs overlap training", "Train ClaimID unavailable")


# =========================================================
# FINAL MODEL CHECK
# =========================================================

final_model = MODEL_FILES["Final Python model"]
add_result("PASS" if final_model.is_file() else "FAIL", "Final Python model exists", str(final_model.relative_to(PROJECT_ROOT)) if final_model.is_file() else "Missing")


# =========================================================
# REPORT
# =========================================================

print("ASSUREX PROJECT AUDIT")
print("PASS/FAIL | Requirement | Actual | Notes")
print("-" * 100)

for result in results:
    print(
        f"{result['status']} | {result['requirement']} | "
        f"{result['actual']} | {result['notes']}"
    )

print("\nSummary:")
print(f"PASS: {sum(result['status'] == 'PASS' for result in results)}")
print(f"FAIL: {sum(result['status'] == 'FAIL' for result in results)}")

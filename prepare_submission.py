from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parent
SUBMISSION_ROOT = PROJECT_ROOT / "submission"

copied_files = []
missing_files = []


def copy_file(source, destination):
    """Copy one existing file and record the result."""

    source = Path(source)

    if not source.is_file():
        missing_files.append(source.relative_to(PROJECT_ROOT))
        return

    destination = SUBMISSION_ROOT / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    copied_files.append(destination.relative_to(SUBMISSION_ROOT))


def copy_directory(source, destination):
    """Copy a directory without changing its source contents."""

    source = Path(source)

    if not source.is_dir():
        missing_files.append(source.relative_to(PROJECT_ROOT))
        return

    for source_file in source.rglob("*"):
        if source_file.is_file():
            relative_file = source_file.relative_to(source)
            copy_file(source_file, Path(destination) / relative_file)


# =========================================================
# DATASET
# =========================================================

copy_file(
    PROJECT_ROOT / "data" / "raw" / "assurex_common_dataset.csv",
    Path("dataset") / "assurex_common_dataset.csv",
)
copy_file(
    PROJECT_ROOT / "data" / "train" / "assurex_train.csv",
    Path("dataset") / "assurex_train.csv",
)
copy_file(
    PROJECT_ROOT / "data" / "validation" / "assurex_validation.csv",
    Path("dataset") / "assurex_validation.csv",
)
copy_file(
    PROJECT_ROOT / "data" / "test" / "assurex_test.csv",
    Path("dataset") / "assurex_test.csv",
)


# =========================================================
# PREPROCESSING
# =========================================================

copy_file(
    PROJECT_ROOT / "preprocessing" / "preprocess.py",
    Path("preprocessing") / "preprocess.py",
)
copy_file(
    PROJECT_ROOT / "data" / "processed" / "train_processed.csv",
    Path("preprocessing") / "train_processed.csv",
)
copy_file(
    PROJECT_ROOT / "data" / "processed" / "validation_processed.csv",
    Path("preprocessing") / "validation_processed.csv",
)
copy_file(
    PROJECT_ROOT / "data" / "processed" / "test_processed.csv",
    Path("preprocessing") / "test_processed.csv",
)


# =========================================================
# PYTHON ML
# =========================================================

python_ml_files = [
    "train_models.py",
    "assurex_final_model.joblib",
    "model_comparison.csv",
    "confusion_matrix.csv",
    "model_info.csv",
    "sample_test_predictions.csv",
]

for file_name in python_ml_files:
    copy_file(
        PROJECT_ROOT / "model" / file_name,
        Path("python_ml") / file_name,
    )


# =========================================================
# GTM
# =========================================================

copy_directory(
    PROJECT_ROOT / "claim_cards",
    Path("gtm") / "claim_cards",
)
copy_directory(
    PROJECT_ROOT / "model" / "gtm_model",
    Path("gtm") / "gtm_model",
)

# Search the whole project for GTM evaluation files.
gtm_evaluation_files = [
    "validation_predictions.csv",
    "validation_confusion_matrix.csv",
    "test_predictions.csv",
    "test_confusion_matrix.csv",
]

for file_name in gtm_evaluation_files:
    matches = [
        path
        for path in PROJECT_ROOT.rglob(file_name)
        if SUBMISSION_ROOT not in path.parents
    ]

    if matches:
        copy_file(
            matches[0],
            Path("gtm") / file_name,
        )
    else:
        missing_files.append(Path(file_name))


# =========================================================
# DECISION ENGINE
# =========================================================

copy_file(
    PROJECT_ROOT / "decision_engine.py",
    Path("decision_engine") / "decision_engine.py",
)

for file_name in [
    "decision_engine_test_results.csv",
    "decision_engine_audit.csv",
]:
    copy_file(
        PROJECT_ROOT / "model" / file_name,
        Path("decision_engine") / file_name,
    )


# =========================================================
# EVALUATION
# =========================================================

for file_name in [
    "final_model_comparison.csv",
    "final_evaluation_report.txt",
]:
    copy_file(
        PROJECT_ROOT / "model" / file_name,
        Path("evaluation") / file_name,
    )

# project_audit.py is a checker, not a generated report. Copy it only when
# a separate audit report file exists in the project.
audit_report_candidates = [
    PROJECT_ROOT / "project_audit.txt",
    PROJECT_ROOT / "project_audit_report.txt",
    PROJECT_ROOT / "model" / "project_audit.txt",
    PROJECT_ROOT / "model" / "project_audit_report.txt",
]

audit_report = next(
    (path for path in audit_report_candidates if path.is_file()),
    None,
)

if audit_report is not None:
    copy_file(
        audit_report,
        Path("evaluation") / audit_report.name,
    )
else:
    missing_files.append(Path("project audit report"))


# =========================================================
# README
# =========================================================

readme_path = SUBMISSION_ROOT / "README.txt"
readme_path.parent.mkdir(parents=True, exist_ok=True)
readme_path.write_text(
    "ASSUREX CLAIM ENGINE SUBMISSION\n"
    "\n"
    "This folder contains copied evidence files for the dataset, preprocessing,\n"
    "Python ML model, GTM model, decision engine, and evaluation results.\n"
    "Original project files were not modified.\n",
    encoding="utf-8",
)
copied_files.append(Path("README.txt"))


# =========================================================
# REPORT
# =========================================================

print("ASSUREX SUBMISSION PREPARATION")
print("=" * 70)
print("Submission folder:")
print(SUBMISSION_ROOT)

print("\nFiles copied:")
for file_path in sorted(copied_files, key=str):
    print(file_path)

print("\nMissing files or reports:")
if missing_files:
    for file_path in sorted(set(missing_files), key=str):
        print(file_path)
else:
    print("None")

print("\nTotal files copied:", len(copied_files))
print("Total missing:", len(set(missing_files)))

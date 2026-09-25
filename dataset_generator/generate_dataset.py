import pandas as pd
import numpy as np

from datetime import datetime
from pathlib import Path


# ============================================================
# ASSUREX CLAIM ENGINE
# COMMON WARRANTY CLAIM DATASET GENERATOR
# ============================================================

# ------------------------------------------------------------
# 1. CONFIGURATION
# ------------------------------------------------------------

RANDOM_SEED = 20260924

TOTAL_RECORDS = 1500

VALID_COUNT = 500
INVALID_COUNT = 500
MANUAL_REVIEW_COUNT = 500

TRAIN_COUNT = 1050
VALIDATION_COUNT = 225
TEST_COUNT = 225


# ------------------------------------------------------------
# 2. RANDOM GENERATOR
# ------------------------------------------------------------

rng = np.random.default_rng(RANDOM_SEED)


# ------------------------------------------------------------
# 3. PROJECT DIRECTORIES
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"
TRAIN_DIR = DATA_DIR / "train"
VALIDATION_DIR = DATA_DIR / "validation"
TEST_DIR = DATA_DIR / "test"

for folder in [
    RAW_DIR,
    TRAIN_DIR,
    VALIDATION_DIR,
    TEST_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 4. MASTER DATA DEFINITIONS
# ------------------------------------------------------------

PRODUCT_CATEGORIES = [
    "Laptop",
    "Smartphone",
    "Television",
    "Refrigerator",
    "Washing Machine",
    "Air Conditioner",
    "Camera",
    "Printer"
]


BRANDS = [
    "Aster",
    "NovaTech",
    "ZenCore",
    "PrimeView",
    "HomePro"
]


FAULT_TYPES = [
    "Power Failure",
    "Display Failure",
    "Battery Problem",
    "Overheating",
    "Water Leakage",
    "Noise",
    "Connectivity Issue",
    "Mechanical Failure"
]


COVERED_DAMAGE_TYPES = [
    "Manufacturing Defect",
    "Electrical Failure"
]


EXCLUDED_DAMAGE_TYPES = [
    "Accidental Damage",
    "Water Damage",
    "Physical Damage",
    "Normal Wear"
]


CLAIM_CHANNELS = [
    "Web",
    "Service Center",
    "Mobile App",
    "Email"
]


REPAIR_OUTCOMES = [
    "Repaired",
    "Part Replaced",
    "No Fault Found",
    "Pending"
]


REPLACED_PARTS = [
    "None",
    "Battery",
    "Display",
    "Main Board",
    "Motor",
    "Power Supply",
    "Cooling Fan"
]


RETAILERS = [
    "Tech World",
    "Digital Plaza",
    "Home Electronics",
    "Smart Store",
    "Mega Retail"
]


SERVICE_CENTERS = [
    "Aster Service Center",
    "NovaTech Service Center",
    "ZenCore Service Center",
    "PrimeView Service Center",
    "Independent Repair Center"
]


# ------------------------------------------------------------
# 5. DATASET SCHEMA
# ------------------------------------------------------------

COLUMNS = [
    "ClaimID",
    "ScenarioID",
    "CustomerID",
    "ProductID",

    "ProductCategory",
    "Brand",
    "ModelNumber",
    "SerialNumber",

    "PurchaseDate",
    "ClaimDate",
    "FaultDate",

    "WarrantyDurationMonths",
    "WarrantyExpiryDate",
    "WarrantyStatus",
    "WarrantyRemainingDays",
    "ExtendedWarranty",

    "FaultType",
    "DamageType",
    "FaultCovered",
    "ClaimReportingWithinPeriod",

    "ReceiptAvailable",
    "WarrantyCardAvailable",
    "ProductImageAvailable",
    "SerialEvidenceAvailable",
    "FaultEvidenceAvailable",
    "RepairReportAvailable",

    "PreviousRepair",
    "RepairCount",
    "RepairAuthorized",

    "PreviousReplacement",
    "ReplacementWithinWarranty",

    "SerialNumberMatch",
    "ProductModelConsistent",

    "DuplicateClaimIndicator",
    "DocumentDuplicateIndicator",
    "ContradictionIndicator",

    "RequiredDocumentsComplete",
    "PurchaseProofAvailable",

    "PriorClaimCount",

    "ClaimAmount",
    "PreviousRepairCost",

    "OCRConfidence",
    "ClaimSubmissionChannel",

    "ClaimClass"
]


# ------------------------------------------------------------
# 6. HELPER FUNCTIONS
# ------------------------------------------------------------

def random_date(start_date, end_date):
    """
    Generate a random date between start_date and end_date.
    """
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    days = (end - start).days

    random_days = int(
        rng.integers(0, days + 1)
    )

    return start + pd.Timedelta(days=random_days)


def add_months(date_value, months):
    """
    Add calendar months to a date.
    """
    return pd.Timestamp(date_value) + pd.DateOffset(
        months=int(months)
    )


def random_choice(values):
    """
    Randomly select one item.
    """
    return values[
        int(rng.integers(0, len(values)))
    ]


def random_bool(probability=0.5):
    """
    Return Yes / No.
    """
    return "Yes" if rng.random() < probability else "No"


def generate_claim_id(index):
    return f"CLM{index:05d}"


def generate_customer_id(index):
    return f"CUS{index:05d}"


def generate_product_id(index):
    return f"PROD{index:05d}"


def generate_serial_number(index):
    return f"SN-2026-{index:06d}"


def generate_model_number(brand, category, index):
    brand_code = brand[:3].upper()
    category_code = category[:3].upper()

    return f"{brand_code}-{category_code}-{index:04d}"


def calculate_product_age_years(purchase_date, claim_date):
    days = (
        pd.Timestamp(claim_date)
        - pd.Timestamp(purchase_date)
    ).days

    return round(days / 365.25, 2)


# ------------------------------------------------------------
# 7. GENERATE BASE CLAIM
# ------------------------------------------------------------

def generate_base_claim(index):

    claim_id = generate_claim_id(index)
    customer_id = generate_customer_id(index)
    product_id = generate_product_id(index)

    product_category = random_choice(
        PRODUCT_CATEGORIES
    )

    brand = random_choice(BRANDS)

    model_number = generate_model_number(
        brand,
        product_category,
        index
    )

    serial_number = generate_serial_number(index)

    purchase_date = random_date(
        "2023-01-01",
        "2026-03-31"
    )

    warranty_duration = random_choice(
        [12, 24, 36]
    )

    warranty_expiry = add_months(
        purchase_date,
        warranty_duration
    )

    # Default claim date after purchase
    claim_date = purchase_date + pd.Timedelta(
        days=int(
            rng.integers(
                30,
                900
            )
        )
    )

    fault_date = claim_date - pd.Timedelta(
        days=int(
            rng.integers(
                1,
                30
            )
        )
    )

    # Prevent fault date before purchase
    if fault_date < purchase_date:
        fault_date = purchase_date + pd.Timedelta(days=1)

    warranty_remaining_days = (
        warranty_expiry - claim_date
    ).days

    if warranty_remaining_days < 0:

        warranty_status = "Expired"

    elif warranty_remaining_days <= 60:

        warranty_status = "Nearing Expiry"

    else:

        warranty_status = "Active"

    extended_warranty = random_bool(0.15)

    fault_type = random_choice(
        FAULT_TYPES
    )

    damage_type = random_choice(
        COVERED_DAMAGE_TYPES + EXCLUDED_DAMAGE_TYPES
    )

    fault_covered = (
        "Yes"
        if damage_type in COVERED_DAMAGE_TYPES
        else "No"
    )

    claim_reporting_within_period = (
        "Yes"
        if (claim_date - fault_date).days <= 30
        else "No"
    )

    receipt_available = random_bool(0.90)
    warranty_card_available = random_bool(0.80)
    product_image_available = random_bool(0.90)
    serial_evidence_available = random_bool(0.90)
    fault_evidence_available = random_bool(0.85)
    repair_report_available = random_bool(0.70)

    previous_repair = random_bool(0.20)

    if previous_repair == "Yes":

        repair_count = int(
            rng.integers(1, 4)
        )

        repair_authorized = random_bool(0.80)

    else:

        repair_count = 0
        repair_authorized = "N/A"

    previous_replacement = random_bool(0.10)

    if previous_replacement == "Yes":

        replacement_within_warranty = random_bool(0.80)

    else:

        replacement_within_warranty = "N/A"

    serial_match = random_bool(0.96)

    product_model_consistent = random_bool(0.96)

    duplicate_claim = random_bool(0.03)

    document_duplicate = random_bool(0.03)

    contradiction = random_bool(0.03)

    required_documents_complete = (
        "Yes"
        if (
            receipt_available == "Yes"
            and warranty_card_available == "Yes"
            and product_image_available == "Yes"
            and serial_evidence_available == "Yes"
            and fault_evidence_available == "Yes"
        )
        else "No"
    )

    purchase_proof_available = (
        "Yes"
        if receipt_available == "Yes"
        else "No"
    )

    prior_claim_count = int(
        rng.integers(0, 4)
    )

    claim_amount = round(
        float(
            rng.uniform(
                50,
                3000
            )
        ),
        2
    )

    if previous_repair == "Yes":

        previous_repair_cost = round(
            float(
                rng.uniform(
                    50,
                    1500
                )
            ),
            2
        )

    else:

        previous_repair_cost = 0.0

    ocr_confidence = round(
        float(
            rng.uniform(
                0.75,
                0.99
            )
        ),
        3
    )

    claim_submission_channel = random_choice(
        CLAIM_CHANNELS
    )

    return {

        "ClaimID": claim_id,
        "ScenarioID": "BASE",
        "CustomerID": customer_id,
        "ProductID": product_id,

        "ProductCategory": product_category,
        "Brand": brand,
        "ModelNumber": model_number,
        "SerialNumber": serial_number,

        "PurchaseDate": purchase_date.strftime("%Y-%m-%d"),
        "ClaimDate": claim_date.strftime("%Y-%m-%d"),
        "FaultDate": fault_date.strftime("%Y-%m-%d"),

        "WarrantyDurationMonths": warranty_duration,
        "WarrantyExpiryDate": warranty_expiry.strftime("%Y-%m-%d"),
        "WarrantyStatus": warranty_status,
        "WarrantyRemainingDays": warranty_remaining_days,
        "ExtendedWarranty": extended_warranty,

        "FaultType": fault_type,
        "DamageType": damage_type,
        "FaultCovered": fault_covered,
        "ClaimReportingWithinPeriod":
            claim_reporting_within_period,

        "ReceiptAvailable": receipt_available,
        "WarrantyCardAvailable":
            warranty_card_available,
        "ProductImageAvailable":
            product_image_available,
        "SerialEvidenceAvailable":
            serial_evidence_available,
        "FaultEvidenceAvailable":
            fault_evidence_available,
        "RepairReportAvailable":
            repair_report_available,

        "PreviousRepair": previous_repair,
        "RepairCount": repair_count,
        "RepairAuthorized": repair_authorized,

        "PreviousReplacement":
            previous_replacement,
        "ReplacementWithinWarranty":
            replacement_within_warranty,

        "SerialNumberMatch": serial_match,
        "ProductModelConsistent":
            product_model_consistent,

        "DuplicateClaimIndicator":
            duplicate_claim,
        "DocumentDuplicateIndicator":
            document_duplicate,
        "ContradictionIndicator":
            contradiction,

        "RequiredDocumentsComplete":
            required_documents_complete,
        "PurchaseProofAvailable":
            purchase_proof_available,

        "PriorClaimCount":
            prior_claim_count,

        "ClaimAmount":
            claim_amount,
        "PreviousRepairCost":
            previous_repair_cost,

        "OCRConfidence":
            ocr_confidence,
        "ClaimSubmissionChannel":
            claim_submission_channel,

        "ClaimClass": None
    }


# ------------------------------------------------------------
# 8. APPLY VALID SCENARIO
# ------------------------------------------------------------

def apply_valid_scenario(record, scenario_number):

    record["ScenarioID"] = (
        f"VALID_{scenario_number:02d}"
    )

    # Warranty must be active
    purchase_date = pd.Timestamp(
        record["PurchaseDate"]
    )

    # Generate claim during warranty
    warranty_months = record[
        "WarrantyDurationMonths"
    ]

    claim_date = add_months(
        purchase_date,
        int(
            rng.integers(
                2,
                max(3, warranty_months - 1)
            )
        )
    )

    fault_date = claim_date - pd.Timedelta(
        days=int(
            rng.integers(
                1,
                15
            )
        )
    )

    warranty_expiry = add_months(
        purchase_date,
        warranty_months
    )

    record["ClaimDate"] = (
        claim_date.strftime("%Y-%m-%d")
    )

    record["FaultDate"] = (
        fault_date.strftime("%Y-%m-%d")
    )

    record["WarrantyExpiryDate"] = (
        warranty_expiry.strftime("%Y-%m-%d")
    )

    record["WarrantyStatus"] = "Active"

    record["WarrantyRemainingDays"] = (
        warranty_expiry - claim_date
    ).days

    # Covered fault
    record["DamageType"] = random_choice(
        COVERED_DAMAGE_TYPES
    )

    record["FaultCovered"] = "Yes"

    record["ClaimReportingWithinPeriod"] = "Yes"

    # Complete documents
    record["ReceiptAvailable"] = "Yes"
    record["WarrantyCardAvailable"] = "Yes"
    record["ProductImageAvailable"] = "Yes"
    record["SerialEvidenceAvailable"] = "Yes"
    record["FaultEvidenceAvailable"] = "Yes"

    # Repair normally absent
    record["PreviousRepair"] = random_bool(0.15)

    if record["PreviousRepair"] == "Yes":

        record["RepairCount"] = int(
            rng.integers(1, 3)
        )

        record["RepairAuthorized"] = "Yes"
        record["RepairReportAvailable"] = "Yes"
        record["PreviousRepairCost"] = round(
            float(
                rng.uniform(
                    50,
                    1000
                )
            ),
            2
        )

    else:

        record["RepairCount"] = 0
        record["RepairAuthorized"] = "N/A"
        record["RepairReportAvailable"] = "No"
        record["PreviousRepairCost"] = 0.0

    record["PreviousReplacement"] = "No"
    record["ReplacementWithinWarranty"] = "N/A"

    # All consistency checks pass
    record["SerialNumberMatch"] = "Yes"
    record["ProductModelConsistent"] = "Yes"

    record["DuplicateClaimIndicator"] = "No"
    record["DocumentDuplicateIndicator"] = "No"
    record["ContradictionIndicator"] = "No"

    record["RequiredDocumentsComplete"] = "Yes"
    record["PurchaseProofAvailable"] = "Yes"

    record["PriorClaimCount"] = int(
        rng.integers(0, 2)
    )

    record["OCRConfidence"] = round(
        float(
            rng.uniform(
                0.90,
                0.99
            )
        ),
        3
    )

    record["ClaimClass"] = "Valid Claim"

    return record


# ------------------------------------------------------------
# 9. APPLY INVALID SCENARIO
# ------------------------------------------------------------

def apply_invalid_scenario(record, scenario_number):

    scenario_types = [
        "EXPIRED_WARRANTY",
        "EXCLUDED_DAMAGE",
        "SERIAL_MISMATCH",
        "UNAUTHORIZED_REPAIR",
        "REPORTING_PERIOD",
        "DUPLICATE_CLAIM"
    ]

    scenario = scenario_types[
        (scenario_number - 1)
        % len(scenario_types)
    ]

    record["ScenarioID"] = (
        f"INVALID_{scenario_number:02d}_{scenario}"
    )

    purchase_date = pd.Timestamp(
        record["PurchaseDate"]
    )

    warranty_months = record[
        "WarrantyDurationMonths"
    ]

    # --------------------------------------------------------
    # 1. EXPIRED WARRANTY
    # --------------------------------------------------------

    if scenario == "EXPIRED_WARRANTY":

        claim_date = add_months(
            purchase_date,
            warranty_months
        ) + pd.Timedelta(days=90)

        fault_date = claim_date - pd.Timedelta(days=10)

        warranty_expiry = add_months(
            purchase_date,
            warranty_months
        )

        record["ClaimDate"] = (
            claim_date.strftime("%Y-%m-%d")
        )

        record["FaultDate"] = (
            fault_date.strftime("%Y-%m-%d")
        )

        record["WarrantyExpiryDate"] = (
            warranty_expiry.strftime("%Y-%m-%d")
        )

        record["WarrantyStatus"] = "Expired"

        record["WarrantyRemainingDays"] = (
            warranty_expiry - claim_date
        ).days

        record["FaultCovered"] = "Yes"
        record["DamageType"] = random_choice(
            COVERED_DAMAGE_TYPES
        )

    # --------------------------------------------------------
    # 2. EXCLUDED DAMAGE
    # --------------------------------------------------------

    elif scenario == "EXCLUDED_DAMAGE":

        record["DamageType"] = random_choice(
            EXCLUDED_DAMAGE_TYPES
        )

        record["FaultCovered"] = "No"

        # Keep warranty active
        claim_date = add_months(
            purchase_date,
            max(
                1,
                int(
                    warranty_months * 0.5
                )
            )
        )

        fault_date = claim_date - pd.Timedelta(days=5)

        record["ClaimDate"] = (
            claim_date.strftime("%Y-%m-%d")
        )

        record["FaultDate"] = (
            fault_date.strftime("%Y-%m-%d")
        )

        warranty_expiry = add_months(
            purchase_date,
            warranty_months
        )

        record["WarrantyExpiryDate"] = (
            warranty_expiry.strftime("%Y-%m-%d")
        )

        record["WarrantyStatus"] = "Active"

        record["WarrantyRemainingDays"] = (
            warranty_expiry - claim_date
        ).days

    # --------------------------------------------------------
    # 3. SERIAL MISMATCH
    # --------------------------------------------------------

    elif scenario == "SERIAL_MISMATCH":

        record["SerialNumberMatch"] = "No"

        record["FaultCovered"] = "Yes"

        record["DamageType"] = random_choice(
            COVERED_DAMAGE_TYPES
        )

        record["WarrantyStatus"] = "Active"

    # --------------------------------------------------------
    # 4. UNAUTHORIZED REPAIR
    # --------------------------------------------------------

    elif scenario == "UNAUTHORIZED_REPAIR":

        record["PreviousRepair"] = "Yes"
        record["RepairCount"] = int(
            rng.integers(1, 3)
        )

        record["RepairAuthorized"] = "No"
        record["RepairReportAvailable"] = "Yes"

        record["PreviousRepairCost"] = round(
            float(
                rng.uniform(
                    100,
                    1200
                )
            ),
            2
        )

        record["FaultCovered"] = "Yes"

        record["DamageType"] = random_choice(
            COVERED_DAMAGE_TYPES
        )

        record["WarrantyStatus"] = "Active"

    # --------------------------------------------------------
    # 5. CLAIM REPORTING PERIOD
    # --------------------------------------------------------

    elif scenario == "REPORTING_PERIOD":

        claim_date = add_months(
            purchase_date,
            max(
                1,
                int(
                    warranty_months * 0.5
                )
            )
        )

        fault_date = claim_date - pd.Timedelta(
            days=60
        )

        record["ClaimDate"] = (
            claim_date.strftime("%Y-%m-%d")
        )

        record["FaultDate"] = (
            fault_date.strftime("%Y-%m-%d")
        )

        record["ClaimReportingWithinPeriod"] = "No"

        record["FaultCovered"] = "Yes"

        record["DamageType"] = random_choice(
            COVERED_DAMAGE_TYPES
        )

        record["WarrantyStatus"] = "Active"

    # --------------------------------------------------------
    # 6. DUPLICATE CLAIM
    # --------------------------------------------------------

    elif scenario == "DUPLICATE_CLAIM":

        record["DuplicateClaimIndicator"] = "Yes"

        record["DocumentDuplicateIndicator"] = "Yes"

        record["PriorClaimCount"] = int(
            rng.integers(1, 4)
        )

        record["FaultCovered"] = "Yes"

        record["DamageType"] = random_choice(
            COVERED_DAMAGE_TYPES
        )

        record["WarrantyStatus"] = "Active"

    # --------------------------------------------------------
    # Common invalid properties
    # --------------------------------------------------------

    record["ClaimClass"] = "Invalid Claim"

    return record


# ------------------------------------------------------------
# 10. APPLY MANUAL REVIEW SCENARIO
# ------------------------------------------------------------

def apply_manual_review_scenario(
    record,
    scenario_number
):

    scenario_types = [
        "MISSING_DOCUMENT",
        "CONTRADICTION",
        "LOW_OCR_CONFIDENCE",
        "SERIAL_WARNING",
        "UNCLEAR_REPAIR",
        "INCOMPLETE_EVIDENCE"
    ]

    scenario = scenario_types[
        (scenario_number - 1)
        % len(scenario_types)
    ]

    record["ScenarioID"] = (
        f"MANUAL_{scenario_number:02d}_{scenario}"
    )

    # --------------------------------------------------------
    # Keep warranty generally active
    # --------------------------------------------------------

    purchase_date = pd.Timestamp(
        record["PurchaseDate"]
    )

    warranty_months = record[
        "WarrantyDurationMonths"
    ]

    claim_date = add_months(
        purchase_date,
        max(
            1,
            int(
                warranty_months * 0.5
            )
        )
    )

    fault_date = claim_date - pd.Timedelta(
        days=int(
            rng.integers(
                1,
                15
            )
        )
    )

    warranty_expiry = add_months(
        purchase_date,
        warranty_months
    )

    record["ClaimDate"] = (
        claim_date.strftime("%Y-%m-%d")
    )

    record["FaultDate"] = (
        fault_date.strftime("%Y-%m-%d")
    )

    record["WarrantyExpiryDate"] = (
        warranty_expiry.strftime("%Y-%m-%d")
    )

    record["WarrantyStatus"] = "Active"

    record["WarrantyRemainingDays"] = (
        warranty_expiry - claim_date
    ).days

    record["FaultCovered"] = "Yes"

    record["DamageType"] = random_choice(
        COVERED_DAMAGE_TYPES
    )

    record["ClaimReportingWithinPeriod"] = "Yes"

    # --------------------------------------------------------
    # Manual review scenario
    # --------------------------------------------------------

    if scenario == "MISSING_DOCUMENT":

        record["ReceiptAvailable"] = "Yes"

        record["WarrantyCardAvailable"] = random_choice(
            ["No", "No", "Yes"]
        )

        record["ProductImageAvailable"] = "Yes"

        record["SerialEvidenceAvailable"] = random_choice(
            ["Yes", "No"]
        )

        record["FaultEvidenceAvailable"] = random_choice(
            ["Yes", "No"]
        )

        record["RepairReportAvailable"] = "No"

        record["RequiredDocumentsComplete"] = "No"

        record["PurchaseProofAvailable"] = "Yes"

    elif scenario == "CONTRADICTION":

        record["ContradictionIndicator"] = "Yes"

        record["ProductModelConsistent"] = "No"

        record["SerialNumberMatch"] = "Yes"

    elif scenario == "LOW_OCR_CONFIDENCE":

        record["OCRConfidence"] = round(
            float(
                rng.uniform(
                    0.45,
                    0.69
                )
            ),
            3
        )

        record["RequiredDocumentsComplete"] = "Yes"

    elif scenario == "SERIAL_WARNING":

        record["SerialNumberMatch"] = "Unknown"

        record["SerialEvidenceAvailable"] = "Yes"

        record["RequiredDocumentsComplete"] = "No"

    elif scenario == "UNCLEAR_REPAIR":

        record["PreviousRepair"] = "Yes"

        record["RepairCount"] = int(
            rng.integers(1, 3)
        )

        record["RepairAuthorized"] = "Unknown"

        record["RepairReportAvailable"] = random_choice(
            ["Yes", "No"]
        )

        record["RequiredDocumentsComplete"] = "No"

    elif scenario == "INCOMPLETE_EVIDENCE":

        record["ProductImageAvailable"] = "Yes"

        record["FaultEvidenceAvailable"] = "No"

        record["SerialEvidenceAvailable"] = "Yes"

        record["RequiredDocumentsComplete"] = "No"

    record["ClaimClass"] = "Manual Review"

    return record


# ------------------------------------------------------------
# 11. GENERATE DATASET
# ------------------------------------------------------------

def generate_dataset():

    records = []

    claim_index = 1

    # --------------------------------------------------------
    # VALID CLAIMS
    # --------------------------------------------------------

    for i in range(1, VALID_COUNT + 1):

        record = generate_base_claim(
            claim_index
        )

        record = apply_valid_scenario(
            record,
            i
        )

        records.append(record)

        claim_index += 1

    # --------------------------------------------------------
    # INVALID CLAIMS
    # --------------------------------------------------------

    for i in range(1, INVALID_COUNT + 1):

        record = generate_base_claim(
            claim_index
        )

        record = apply_invalid_scenario(
            record,
            i
        )

        records.append(record)

        claim_index += 1

    # --------------------------------------------------------
    # MANUAL REVIEW CLAIMS
    # --------------------------------------------------------

    for i in range(
        1,
        MANUAL_REVIEW_COUNT + 1
    ):

        record = generate_base_claim(
            claim_index
        )

        record = apply_manual_review_scenario(
            record,
            i
        )

        records.append(record)

        claim_index += 1

    df = pd.DataFrame(
        records,
        columns=COLUMNS
    )

    return df


# ------------------------------------------------------------
# 12. VALIDATE DATASET
# ------------------------------------------------------------

def validate_dataset(df):

    print("\n")
    print("=" * 60)
    print("DATASET VALIDATION")
    print("=" * 60)

    # Total records
    assert len(df) == TOTAL_RECORDS, (
        f"Expected {TOTAL_RECORDS}, "
        f"got {len(df)}"
    )

    print("PASS - Total records:", len(df))

    # Required columns
    missing_columns = [
        column
        for column in COLUMNS
        if column not in df.columns
    ]

    assert not missing_columns, (
        f"Missing columns: {missing_columns}"
    )

    print(
        "PASS - All required columns exist"
    )

    # Class counts
    class_counts = (
        df["ClaimClass"]
        .value_counts()
        .to_dict()
    )

    assert class_counts.get(
        "Valid Claim", 0
    ) == VALID_COUNT

    assert class_counts.get(
        "Invalid Claim", 0
    ) == INVALID_COUNT

    assert class_counts.get(
        "Manual Review", 0
    ) == MANUAL_REVIEW_COUNT

    print(
        "PASS - Class distribution is 500 / 500 / 500"
    )

    # Unique Claim IDs
    assert df["ClaimID"].is_unique

    print(
        "PASS - Claim IDs are unique"
    )

    # Missing Claim IDs
    assert not df["ClaimID"].isna().any()

    print(
        "PASS - No missing Claim IDs"
    )

    # Valid claims should not have hard-fail flags
    valid_df = df[
        df["ClaimClass"] == "Valid Claim"
    ]

    assert (
        valid_df["SerialNumberMatch"] == "Yes"
    ).all()

    assert (
        valid_df["DuplicateClaimIndicator"] == "No"
    ).all()

    assert (
        valid_df["DocumentDuplicateIndicator"] == "No"
    ).all()

    assert (
        valid_df["ContradictionIndicator"] == "No"
    ).all()

    print(
        "PASS - Valid claims contain no hard-fail indicators"
    )

    # Invalid claims
    invalid_df = df[
        df["ClaimClass"] == "Invalid Claim"
    ]

    invalid_condition = (
        (invalid_df["WarrantyStatus"] == "Expired")
        |
        (invalid_df["FaultCovered"] == "No")
        |
        (invalid_df["SerialNumberMatch"] == "No")
        |
        (invalid_df["RepairAuthorized"] == "No")
        |
        (invalid_df["ClaimReportingWithinPeriod"] == "No")
        |
        (invalid_df["DuplicateClaimIndicator"] == "Yes")
    )

    assert invalid_condition.all()

    print(
        "PASS - Invalid claims contain at least one invalid condition"
    )

    # Manual review
    manual_df = df[
        df["ClaimClass"] == "Manual Review"
    ]

    manual_condition = (
        (manual_df["RequiredDocumentsComplete"] == "No")
        |
        (manual_df["ContradictionIndicator"] == "Yes")
        |
        (manual_df["OCRConfidence"] < 0.70)
        |
        (manual_df["SerialNumberMatch"] == "Unknown")
        |
        (manual_df["RepairAuthorized"] == "Unknown")
    )

    assert manual_condition.all()

    print(
        "PASS - Manual Review claims contain review indicators"
    )

    print("=" * 60)


# ------------------------------------------------------------
# 13. STRATIFIED SPLIT
# ------------------------------------------------------------

def stratified_split(df):

    train_parts = []
    validation_parts = []
    test_parts = []

    for class_name in [
        "Valid Claim",
        "Invalid Claim",
        "Manual Review"
    ]:

        class_df = df[
            df["ClaimClass"] == class_name
        ].copy()

        # Shuffle deterministically
        class_df = class_df.sample(
            frac=1,
            random_state=RANDOM_SEED
        ).reset_index(drop=True)

        # 350 train
        train = class_df.iloc[
            :350
        ].copy()

        # 75 validation
        validation = class_df.iloc[
            350:425
        ].copy()

        # 75 test
        test = class_df.iloc[
            425:500
        ].copy()

        train_parts.append(train)
        validation_parts.append(validation)
        test_parts.append(test)

    train_df = pd.concat(
        train_parts,
        ignore_index=True
    )

    validation_df = pd.concat(
        validation_parts,
        ignore_index=True
    )

    test_df = pd.concat(
        test_parts,
        ignore_index=True
    )

    # Shuffle each split again
    train_df = train_df.sample(
        frac=1,
        random_state=RANDOM_SEED
    ).reset_index(drop=True)

    validation_df = validation_df.sample(
        frac=1,
        random_state=RANDOM_SEED
    ).reset_index(drop=True)

    test_df = test_df.sample(
        frac=1,
        random_state=RANDOM_SEED
    ).reset_index(drop=True)

    return (
        train_df,
        validation_df,
        test_df
    )


# ------------------------------------------------------------
# 14. VALIDATE SPLITS
# ------------------------------------------------------------

def validate_splits(
    train_df,
    validation_df,
    test_df
):

    print("\n")
    print("=" * 60)
    print("SPLIT VALIDATION")
    print("=" * 60)

    assert len(train_df) == TRAIN_COUNT
    assert len(validation_df) == VALIDATION_COUNT
    assert len(test_df) == TEST_COUNT

    print(
        f"PASS - Train: {len(train_df)}"
    )

    print(
        f"PASS - Validation: {len(validation_df)}"
    )

    print(
        f"PASS - Test: {len(test_df)}"
    )

    # Check class balance
    for name, split_df in [
        ("Train", train_df),
        ("Validation", validation_df),
        ("Test", test_df)
    ]:

        counts = (
            split_df["ClaimClass"]
            .value_counts()
            .to_dict()
        )

        print(
            f"{name}: "
            f"Valid={counts.get('Valid Claim', 0)}, "
            f"Invalid={counts.get('Invalid Claim', 0)}, "
            f"Manual={counts.get('Manual Review', 0)}"
        )

    # Check no overlap
    train_ids = set(
        train_df["ClaimID"]
    )

    validation_ids = set(
        validation_df["ClaimID"]
    )

    test_ids = set(
        test_df["ClaimID"]
    )

    assert train_ids.isdisjoint(
        validation_ids
    )

    assert train_ids.isdisjoint(
        test_ids
    )

    assert validation_ids.isdisjoint(
        test_ids
    )

    print(
        "PASS - No Claim ID overlap between splits"
    )

    print("=" * 60)


# ------------------------------------------------------------
# 15. DATA DICTIONARY
# ------------------------------------------------------------

def create_data_dictionary():

    dictionary = [

        ("ClaimID",
         "Unique identifier for the warranty claim",
         "Metadata"),

        ("ScenarioID",
         "Synthetic scenario used to generate the claim",
         "Metadata - do not use as ML feature"),

        ("CustomerID",
         "Unique customer identifier",
         "Identifier"),

        ("ProductID",
         "Unique product identifier",
         "Identifier"),

        ("ProductCategory",
         "Product category",
         "Categorical"),

        ("Brand",
         "Product brand",
         "Categorical"),

        ("ModelNumber",
         "Product model number",
         "Categorical"),

        ("SerialNumber",
         "Product serial number",
         "Identifier"),

        ("PurchaseDate",
         "Date when product was purchased",
         "Date"),

        ("ClaimDate",
         "Date when warranty claim was submitted",
         "Date"),

        ("FaultDate",
         "Date when fault occurred",
         "Date"),

        ("WarrantyDurationMonths",
         "Warranty duration in months",
         "Numerical"),

        ("WarrantyExpiryDate",
         "Calculated warranty expiry date",
         "Date"),

        ("WarrantyStatus",
         "Active, Nearing Expiry, or Expired",
         "Categorical"),

        ("WarrantyRemainingDays",
         "Remaining warranty period in days",
         "Numerical"),

        ("ExtendedWarranty",
         "Whether extended warranty exists",
         "Binary"),

        ("FaultType",
         "Reported fault type",
         "Categorical"),

        ("DamageType",
         "Type of damage or failure",
         "Categorical"),

        ("FaultCovered",
         "Whether fault is covered by warranty",
         "Binary"),

        ("ClaimReportingWithinPeriod",
         "Whether claim was reported within allowed period",
         "Binary"),

        ("ReceiptAvailable",
         "Purchase receipt availability",
         "Binary"),

        ("WarrantyCardAvailable",
         "Warranty card availability",
         "Binary"),

        ("ProductImageAvailable",
         "Product image availability",
         "Binary"),

        ("SerialEvidenceAvailable",
         "Serial-number evidence availability",
         "Binary"),

        ("FaultEvidenceAvailable",
         "Fault evidence availability",
         "Binary"),

        ("RepairReportAvailable",
         "Repair report availability",
         "Binary"),

        ("PreviousRepair",
         "Whether product was repaired before",
         "Binary"),

        ("RepairCount",
         "Number of previous repairs",
         "Numerical"),

        ("RepairAuthorized",
         "Whether previous repair was authorized",
         "Categorical"),

        ("PreviousReplacement",
         "Whether product was previously replaced",
         "Binary"),

        ("ReplacementWithinWarranty",
         "Whether replacement occurred within warranty",
         "Categorical"),

        ("SerialNumberMatch",
         "Serial number consistency result",
         "Categorical"),

        ("ProductModelConsistent",
         "Whether product model information is consistent",
         "Binary"),

        ("DuplicateClaimIndicator",
         "Possible duplicate claim indicator",
         "Binary"),

        ("DocumentDuplicateIndicator",
         "Possible duplicate document indicator",
         "Binary"),

        ("ContradictionIndicator",
         "Whether contradictory information was detected",
         "Binary"),

        ("RequiredDocumentsComplete",
         "Whether required claim documents are complete",
         "Binary"),

        ("PurchaseProofAvailable",
         "Whether purchase proof is available",
         "Binary"),

        ("PriorClaimCount",
         "Number of previous claims",
         "Numerical"),

        ("ClaimAmount",
         "Claimed amount",
         "Numerical"),

        ("PreviousRepairCost",
         "Cost of previous repair",
         "Numerical"),

        ("OCRConfidence",
         "Confidence of OCR extraction",
         "Numerical"),

        ("ClaimSubmissionChannel",
         "Channel used to submit claim",
         "Categorical"),

        ("ClaimClass",
         "Target class: Valid Claim, Invalid Claim, Manual Review",
         "TARGET")

    ]

    dictionary_df = pd.DataFrame(
        dictionary,
        columns=[
            "ColumnName",
            "Description",
            "DataTypeOrRole"
        ]
    )

    return dictionary_df


# ------------------------------------------------------------
# 16. DATASET STATISTICS
# ------------------------------------------------------------

def create_statistics(
    df,
    train_df,
    validation_df,
    test_df
):

    statistics = []

    statistics.append(
        {
            "Metric": "Total Records",
            "Value": len(df)
        }
    )

    statistics.append(
        {
            "Metric": "Valid Claim",
            "Value": (
                df["ClaimClass"]
                .eq("Valid Claim")
                .sum()
            )
        }
    )

    statistics.append(
        {
            "Metric": "Invalid Claim",
            "Value": (
                df["ClaimClass"]
                .eq("Invalid Claim")
                .sum()
            )
        }
    )

    statistics.append(
        {
            "Metric": "Manual Review",
            "Value": (
                df["ClaimClass"]
                .eq("Manual Review")
                .sum()
            )
        }
    )

    statistics.append(
        {
            "Metric": "Training Records",
            "Value": len(train_df)
        }
    )

    statistics.append(
        {
            "Metric": "Validation Records",
            "Value": len(validation_df)
        }
    )

    statistics.append(
        {
            "Metric": "Testing Records",
            "Value": len(test_df)
        }
    )

    statistics.append(
        {
            "Metric": "Unique Claim IDs",
            "Value": df["ClaimID"].nunique()
        }
    )

    statistics_df = pd.DataFrame(
        statistics
    )

    return statistics_df


# ------------------------------------------------------------
# 17. SAVE DATASET
# ------------------------------------------------------------

def save_dataset(
    df,
    train_df,
    validation_df,
    test_df
):

    common_path = (
        RAW_DIR /
        "assurex_common_dataset.csv"
    )

    train_path = (
        TRAIN_DIR /
        "assurex_train.csv"
    )

    validation_path = (
        VALIDATION_DIR /
        "assurex_validation.csv"
    )

    test_path = (
        TEST_DIR /
        "assurex_test.csv"
    )

    dictionary_path = (
        DATA_DIR /
        "assurex_data_dictionary.csv"
    )

    statistics_path = (
        DATA_DIR /
        "assurex_dataset_statistics.csv"
    )

    # Save CSV
    df.to_csv(
        common_path,
        index=False,
        encoding="utf-8-sig"
    )

    train_df.to_csv(
        train_path,
        index=False,
        encoding="utf-8-sig"
    )

    validation_df.to_csv(
        validation_path,
        index=False,
        encoding="utf-8-sig"
    )

    test_df.to_csv(
        test_path,
        index=False,
        encoding="utf-8-sig"
    )

    # Data dictionary
    dictionary_df = create_data_dictionary()

    dictionary_df.to_csv(
        dictionary_path,
        index=False,
        encoding="utf-8-sig"
    )

    # Statistics
    statistics_df = create_statistics(
        df,
        train_df,
        validation_df,
        test_df
    )

    statistics_df.to_csv(
        statistics_path,
        index=False,
        encoding="utf-8-sig"
    )

    return (
        common_path,
        train_path,
        validation_path,
        test_path,
        dictionary_path,
        statistics_path
    )


# ------------------------------------------------------------
# 18. PRINT SUMMARY
# ------------------------------------------------------------

def print_final_summary(
    df,
    train_df,
    validation_df,
    test_df
):

    print("\n")
    print("=" * 60)
    print("ASSUREX DATASET GENERATION COMPLETED")
    print("=" * 60)

    print(
        f"Total records      : {len(df)}"
    )

    print(
        f"Valid Claim        : "
        f"{(df['ClaimClass'] == 'Valid Claim').sum()}"
    )

    print(
        f"Invalid Claim      : "
        f"{(df['ClaimClass'] == 'Invalid Claim').sum()}"
    )

    print(
        f"Manual Review      : "
        f"{(df['ClaimClass'] == 'Manual Review').sum()}"
    )

    print("-" * 60)

    print(
        f"Training           : {len(train_df)}"
    )

    print(
        f"Validation         : {len(validation_df)}"
    )

    print(
        f"Testing            : {len(test_df)}"
    )

    print("-" * 60)

    print("Files generated:")

    print(
        "1.",
        RAW_DIR /
        "assurex_common_dataset.csv"
    )

    print(
        "2.",
        TRAIN_DIR /
        "assurex_train.csv"
    )

    print(
        "3.",
        VALIDATION_DIR /
        "assurex_validation.csv"
    )

    print(
        "4.",
        TEST_DIR /
        "assurex_test.csv"
    )

    print(
        "5.",
        DATA_DIR /
        "assurex_data_dictionary.csv"
    )

    print(
        "6.",
        DATA_DIR /
        "assurex_dataset_statistics.csv"
    )

    print("=" * 60)


# ------------------------------------------------------------
# 19. MAIN PROGRAM
# ------------------------------------------------------------

def main():

    print("\n")
    print("=" * 60)
    print("ASSUREX CLAIM ENGINE")
    print("COMMON DATASET GENERATOR")
    print("=" * 60)

    print(
        f"Random Seed: {RANDOM_SEED}"
    )

    print(
        "Generating 1,500 claims..."
    )

    # Generate
    df = generate_dataset()

    # Validate
    validate_dataset(df)

    # Split
    (
        train_df,
        validation_df,
        test_df
    ) = stratified_split(df)

    # Validate split
    validate_splits(
        train_df,
        validation_df,
        test_df
    )

    # Save
    save_dataset(
        df,
        train_df,
        validation_df,
        test_df
    )

    # Summary
    print_final_summary(
        df,
        train_df,
        validation_df,
        test_df
    )


# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------

if __name__ == "__main__":
    main()
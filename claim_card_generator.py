import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# ASSUREX CLAIM ENGINE
# CLAIM SUMMARY CARD GENERATOR
# ============================================================

print("=" * 60)
print("ASSUREX CLAIM SUMMARY CARD GENERATOR")
print("=" * 60)


# ============================================================
# 1. FILE DATA
# ============================================================

TRAIN_FILE = "data/train/assurex_train.csv"
VALIDATION_FILE = "data/validation/assurex_validation.csv"
TEST_FILE = "data/test/assurex_test.csv"

OUTPUT_FOLDER = Path("claim_cards")


# ============================================================
# 2. IMAGE SETTINGS
# ============================================================

WIDTH = 1200
HEIGHT = 1500

BACKGROUND = (245, 247, 250)
DARK = (30, 41, 59)
GRAY = (71, 85, 105)
LIGHT = (226, 232, 240)
WHITE = (255, 255, 255)


# ============================================================
# 3. FONT
# ============================================================

def get_font(size, bold=False):

    if bold:
        paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf"
        ]
    else:
        paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf"
        ]

    for path in paths:

        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


TITLE_FONT = get_font(40, True)
SECTION_FONT = get_font(25, True)
LABEL_FONT = get_font(20, True)
VALUE_FONT = get_font(20, False)
SMALL_FONT = get_font(17, False)


# ============================================================
# 4. HELPER
# ============================================================

def value(row, column):

    if column not in row.index:
        return "N/A"

    result = row[column]

    if pd.isna(result):
        return "N/A"

    return str(result)


def date_value(row, column):

    result = value(row, column)

    if result == "N/A":
        return result

    try:
        return pd.to_datetime(result).strftime("%Y-%m-%d")
    except:
        return result


def draw_field(draw, x, y, label, content):

    draw.text(
        (x, y),
        label,
        font=LABEL_FONT,
        fill=GRAY
    )

    draw.text(
        (x + 280, y),
        content,
        font=VALUE_FONT,
        fill=DARK
    )


def draw_section(draw, y, title):

    draw.text(
        (60, y),
        title,
        font=SECTION_FONT,
        fill=DARK
    )

    draw.line(
        (60, y + 38, WIDTH - 60, y + 38),
        fill=LIGHT,
        width=2
    )


# ============================================================
# 5. LAYOUT A
# ============================================================

def create_layout_a(row, output_file):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BACKGROUND
    )

    draw = ImageDraw.Draw(image)

    # HEADER

    draw.rectangle(
        (0, 0, WIDTH, 140),
        fill=DARK
    )

    draw.text(
        (60, 25),
        "ASSUREX CLAIM SUMMARY",
        font=TITLE_FONT,
        fill=WHITE
    )

    draw.text(
        (60, 85),
        "Claim ID: " + value(row, "ClaimID"),
        font=SMALL_FONT,
        fill=WHITE
    )

    y = 180

    # CLAIM

    draw_section(
        draw,
        y,
        "CLAIM INFORMATION"
    )

    y += 60

    fields = [
        ("Customer ID:", "CustomerID"),
        ("Product ID:", "ProductID"),
        ("Category:", "ProductCategory"),
        ("Brand:", "Brand"),
        ("Model:", "ModelNumber"),
        ("Purchase Date:", "PurchaseDate"),
        ("Claim Date:", "ClaimDate"),
    ]

    for label, column in fields:

        if "Date" in label:
            text = date_value(row, column)
        else:
            text = value(row, column)

        draw_field(
            draw,
            60,
            y,
            label,
            text
        )

        y += 40

    # FAULT

    y += 25

    draw_section(
        draw,
        y,
        "FAULT INFORMATION"
    )

    y += 60

    fields = [
        ("Fault Type:", "FaultType"),
        ("Damage Type:", "DamageType"),
        ("Fault Covered:", "FaultCovered"),
        ("Reporting Period:", "ClaimReportingWithinPeriod"),
    ]

    for label, column in fields:

        draw_field(
            draw,
            60,
            y,
            label,
            value(row, column)
        )

        y += 40

    # WARRANTY

    y += 25

    draw_section(
        draw,
        y,
        "WARRANTY"
    )

    y += 60

    fields = [
        ("Duration:", "WarrantyDurationMonths"),
        ("Status:", "WarrantyStatus"),
        ("Remaining Days:", "WarrantyRemainingDays"),
        ("Extended:", "ExtendedWarranty"),
    ]

    for label, column in fields:

        draw_field(
            draw,
            60,
            y,
            label,
            value(row, column)
        )

        y += 40

    # DOCUMENTS

    y += 25

    draw_section(
        draw,
        y,
        "DOCUMENT EVIDENCE"
    )

    y += 60

    fields = [
        ("Receipt:", "ReceiptAvailable"),
        ("Warranty Card:", "WarrantyCardAvailable"),
        ("Product Image:", "ProductImageAvailable"),
        ("Serial Evidence:", "SerialEvidenceAvailable"),
        ("Fault Evidence:", "FaultEvidenceAvailable"),
        ("Repair Report:", "RepairReportAvailable"),
    ]

    for label, column in fields:

        draw_field(
            draw,
            60,
            y,
            label,
            value(row, column)
        )

        y += 34

    # DATASET CLASS

    y += 25

    draw.rectangle(
        (60, y, WIDTH - 60, y + 65),
        fill=DARK
    )

    draw.text(
        (80, y + 17),
        "DATASET CLASS: " + value(row, "ClaimClass"),
        font=SECTION_FONT,
        fill=WHITE
    )

    image.save(output_file)


# ============================================================
# 6. LAYOUT B
# ============================================================

def create_layout_b(row, output_file):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BACKGROUND
    )

    draw = ImageDraw.Draw(image)

    # HEADER

    draw.rectangle(
        (0, 0, WIDTH, 180),
        fill=DARK
    )

    draw.text(
        (60, 30),
        "ASSUREX",
        font=TITLE_FONT,
        fill=WHITE
    )

    draw.text(
        (60, 90),
        "CLAIM SUMMARY CARD",
        font=SECTION_FONT,
        fill=WHITE
    )

    draw.text(
        (750, 45),
        "CLAIM ID",
        font=SMALL_FONT,
        fill=WHITE
    )

    draw.text(
        (750, 75),
        value(row, "ClaimID"),
        font=LABEL_FONT,
        fill=WHITE
    )

    y = 220

    # PRODUCT BOX

    draw.rounded_rectangle(
        (60, y, WIDTH - 60, y + 210),
        radius=15,
        outline=LIGHT,
        width=3,
        fill=WHITE
    )

    draw.text(
        (90, y + 25),
        "PRODUCT",
        font=SECTION_FONT,
        fill=DARK
    )

    draw_field(
        draw,
        90,
        y + 75,
        "Category:",
        value(row, "ProductCategory")
    )

    draw_field(
        draw,
        90,
        y + 115,
        "Brand:",
        value(row, "Brand")
    )

    draw_field(
        draw,
        90,
        y + 155,
        "Model:",
        value(row, "ModelNumber")
    )

    y += 240

    # WARRANTY + FAULT

    draw.rounded_rectangle(
        (60, y, 570, y + 300),
        radius=15,
        outline=LIGHT,
        width=3,
        fill=WHITE
    )

    draw.rounded_rectangle(
        (630, y, WIDTH - 60, y + 300),
        radius=15,
        outline=LIGHT,
        width=3,
        fill=WHITE
    )

    draw.text(
        (90, y + 25),
        "WARRANTY",
        font=SECTION_FONT,
        fill=DARK
    )

    draw.text(
        (660, y + 25),
        "FAULT",
        font=SECTION_FONT,
        fill=DARK
    )

    warranty = [
        ("Status:", "WarrantyStatus"),
        ("Duration:", "WarrantyDurationMonths"),
        ("Remaining:", "WarrantyRemainingDays"),
        ("Extended:", "ExtendedWarranty"),
    ]

    yy = y + 80

    for label, column in warranty:

        draw.text(
            (90, yy),
            label,
            font=LABEL_FONT,
            fill=GRAY
        )

        draw.text(
            (270, yy),
            value(row, column),
            font=VALUE_FONT,
            fill=DARK
        )

        yy += 45

    fault = [
        ("Type:", "FaultType"),
        ("Damage:", "DamageType"),
        ("Covered:", "FaultCovered"),
        ("Report:", "ClaimReportingWithinPeriod"),
    ]

    yy = y + 80

    for label, column in fault:

        draw.text(
            (660, yy),
            label,
            font=LABEL_FONT,
            fill=GRAY
        )

        draw.text(
            (820, yy),
            value(row, column),
            font=VALUE_FONT,
            fill=DARK
        )

        yy += 45

    y += 330

    # DOCUMENTS

    draw.rounded_rectangle(
        (60, y, WIDTH - 60, y + 350),
        radius=15,
        outline=LIGHT,
        width=3,
        fill=WHITE
    )

    draw.text(
        (90, y + 25),
        "DOCUMENT & EVIDENCE",
        font=SECTION_FONT,
        fill=DARK
    )

    documents = [
        ("Receipt:", "ReceiptAvailable"),
        ("Warranty Card:", "WarrantyCardAvailable"),
        ("Product Image:", "ProductImageAvailable"),
        ("Serial Evidence:", "SerialEvidenceAvailable"),
        ("Fault Evidence:", "FaultEvidenceAvailable"),
        ("Repair Report:", "RepairReportAvailable"),
        ("Required Documents:", "RequiredDocumentsComplete"),
    ]

    yy = y + 80

    for label, column in documents:

        draw.text(
            (90, yy),
            label,
            font=LABEL_FONT,
            fill=GRAY
        )

        draw.text(
            (390, yy),
            value(row, column),
            font=VALUE_FONT,
            fill=DARK
        )

        yy += 35

    y += 380

    # HISTORY

    draw.rounded_rectangle(
        (60, y, WIDTH - 60, y + 260),
        radius=15,
        outline=LIGHT,
        width=3,
        fill=WHITE
    )

    draw.text(
        (90, y + 25),
        "HISTORY & CONSISTENCY",
        font=SECTION_FONT,
        fill=DARK
    )

    history = [
        ("Previous Repair:", "PreviousRepair"),
        ("Repair Count:", "RepairCount"),
        ("Repair Authorized:", "RepairAuthorized"),
        ("Serial Match:", "SerialNumberMatch"),
        ("Duplicate:", "DuplicateClaimIndicator"),
        ("Contradiction:", "ContradictionIndicator"),
    ]

    yy = y + 80

    for label, column in history:

        draw.text(
            (90, yy),
            label,
            font=LABEL_FONT,
            fill=GRAY
        )

        draw.text(
            (390, yy),
            value(row, column),
            font=VALUE_FONT,
            fill=DARK
        )

        yy += 32

    # DATASET CLASS

    y += 290

    draw.rectangle(
        (60, y, WIDTH - 60, y + 65),
        fill=DARK
    )

    draw.text(
        (80, y + 17),
        "DATASET CLASS: " + value(row, "ClaimClass"),
        font=SECTION_FONT,
        fill=WHITE
    )

    image.save(output_file)


# ============================================================
# 7. GENERATE CARDS
# ============================================================

def generate_cards(csv_file, split, variations):

    print("\nGenerating:", split)

    df = pd.read_csv(csv_file)

    for _, row in df.iterrows():

        claim_id = value(row, "ClaimID")

        # Variation 01
        if variations >= 1:

            folder = (
                OUTPUT_FOLDER
                / split
                / "variation_01"
            )

            folder.mkdir(
                parents=True,
                exist_ok=True
            )

            file = (
                folder
                / f"{claim_id}_v01.png"
            )

            create_layout_a(
                row,
                file
            )

        # Variation 02
        if variations >= 2:

            folder = (
                OUTPUT_FOLDER
                / split
                / "variation_02"
            )

            folder.mkdir(
                parents=True,
                exist_ok=True
            )

            file = (
                folder
                / f"{claim_id}_v02.png"
            )

            create_layout_b(
                row,
                file
            )


    print(
        "Completed:",
        len(df),
        "claims"
    )


# ============================================================
# 8. START
# ============================================================

generate_cards(
    TRAIN_FILE,
    "train",
    2
)

generate_cards(
    VALIDATION_FILE,
    "validation",
    1
)

generate_cards(
    TEST_FILE,
    "test",
    1
)


# ============================================================
# FINISH
# ============================================================

print("\n")
print("=" * 60)
print("DONE")
print("=" * 60)

print(
    "Training     : 2100 images"
)

print(
    "Validation   : 225 images"
)

print(
    "Test         : 225 images"
)

print(
    "Total        : 2550 images"
)

print("=" * 60)
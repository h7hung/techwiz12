from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_PATH = Path(__file__).resolve().parent / "assurex.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_claim_columns() -> None:
    """Add newly supported raw claim fields to an existing SQLite database."""
    required_columns = {
        "scenario_id": "VARCHAR",
        "product_id": "VARCHAR",
        "purchase_date": "DATE",
        "claim_date": "DATE",
        "fault_date": "DATE",
        "warranty_duration_months": "INTEGER",
        "warranty_expiry_date": "DATE",
        "warranty_remaining_days": "INTEGER",
        "extended_warranty": "VARCHAR",
        "claim_reporting_within_period": "VARCHAR",
        "repair_count": "INTEGER",
        "replacement_within_warranty": "VARCHAR",
        "required_documents_complete": "VARCHAR",
        "purchase_proof_available": "VARCHAR",
        "prior_claim_count": "INTEGER",
        "previous_repair_cost": "FLOAT",
        "ocr_confidence": "FLOAT",
        "claim_submission_channel": "VARCHAR",
    }
    existing_columns = {
        column["name"] for column in inspect(engine).get_columns("claims")
    }
    with engine.begin() as connection:
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE claims ADD COLUMN "
                        f"{column_name} {column_type}"
                    )
                )

from contextlib import asynccontextmanager
from typing import Iterator

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database import Base, engine, ensure_claim_columns, get_db
import models
from routes.claims import router as claims_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_claim_columns()
    yield


app = FastAPI(
    title="AssureX Claim Engine",
    lifespan=lifespan,
)

app.include_router(claims_router)


@app.get("/api/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    return {
        "status": "ok",
        "service": "AssureX Claim Engine",
    }

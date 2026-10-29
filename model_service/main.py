"""
Serwis inferencji: wczytuje artefakt modelu i zwraca PD dla wniosku.
Uruchamianie z korzenia repo: uvicorn model_service.main:app --reload
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from model_service.schemas import HealthResponse, ScoreRequest, ScoreResponse

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = REPO_ROOT / "artifacts" / "credit_model_v1.joblib"
MODEL_PATH = Path(os.environ.get("MODEL_PATH", DEFAULT_MODEL_PATH))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Przy starcie wczytuje artefakt do app.state; przy błędzie serwis wstaje jako degraded."""
    try:
        app.state.artifact = joblib.load(MODEL_PATH)
    except FileNotFoundError as e:
        app.state.artifact = None
        print(f"ERROR loading {MODEL_PATH}: {e}")
    yield


app = FastAPI(title="Credit scoring service", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health():
    """Zwraca stan serwisu i wersję wczytanego modelu."""
    artifact = app.state.artifact

    if artifact is not None:
        return HealthResponse(
        status = "ok",
        model_loaded = True,
        model_version = artifact["model_version"]
    )
    else:
        return HealthResponse(status="degraded", model_loaded=False)


@app.post("/score", response_model=ScoreResponse)
def score(request: ScoreRequest):
    """Liczy PD dla jednego wniosku."""
    artifact = app.state.artifact

    if artifact is None:
        raise HTTPException(status_code=503, detail="Model is not loaded. Please try again later.")

    df = pd.DataFrame([request.model_dump()])
    pipeline = artifact['pipeline']
    pd_value = float(pipeline.predict_proba(df)[:, 1][0])

    return ScoreResponse(probability_of_default = pd_value, model_version = artifact["model_version"])
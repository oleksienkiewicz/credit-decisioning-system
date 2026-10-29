from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class ScoreRequest(BaseModel):
    """Wejście endpointu POST /score."""

    model_config = ConfigDict(extra="forbid")

    income: float = Field(gt=0)
    credit_amount: float = Field(gt=0)
    num_installments: float = Field(ge=8, le=46)
    age_years: float = Field(ge=20, le=70)
    employment_years: float | None = Field(default=None, ge=0)
    income_type: Literal["Working", "Commercial associate", "Pensioner", "State servant", "Other"]
    education: Literal["Secondary / secondary special", "Higher education", "Incomplete higher", "Lower secondary", "Academic degree"]
    ext_score_2: float | None = Field(default=None, ge=0, le=1)
    ext_score_3: float | None = Field(default=None, ge=0, le=1)

class ScoreResponse(BaseModel):
    """
    Wyjście endpointu POST /score
    """
    probability_of_default: float = Field(ge=0, le=1)
    model_version: str

class HealthResponse(BaseModel):
    """
    Wyjście endpointu GET /health.
    """
    status: Literal["ok", "degraded"]
    model_loaded: bool
    model_version: str | None = None
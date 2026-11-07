"""Klient serwisu inferencji: wysyła wniosek do FastAPI i zwraca PD."""

from decimal import Decimal
import httpx
from django.conf import settings

SCORING_FIELDS = ["income", "credit_amount", "num_installments", "age_years", "employment_years", "income_type", "education", "ext_score_2", "ext_score_3"]

TIMEOUT_SECONDS = 5.0


def build_payload(application):
    """Zamienia wniosek z bazy na słownik JSON zgodny z kontraktem FastAPI."""
    payload = {}
    for name in SCORING_FIELDS:
        value = getattr(application, name)
        if isinstance(value, (Decimal, int)):
            value = float(value)
        payload[name] = value

    return payload
        


def score_application(application):
    """Wysyła wniosek do /score. Zwraca słownik z wynikiem albo None, gdy się nie udało."""
    try:
        response = httpx.post(f"{settings.MODEL_SERVICE_URL}/score",
                            json=build_payload(application), timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        print(f"Scoring failed: {e}")
        return None

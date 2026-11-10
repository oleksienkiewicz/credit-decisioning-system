from django import forms

from .models import LoanApplication
from .scoring_client import SCORING_FIELDS


class LoanApplicationForm(forms.ModelForm):
    """Formularz wniosku: 9 pól wejściowych modelu + reguły między polami."""

    class Meta:
        model = LoanApplication
        fields = SCORING_FIELDS

    def clean(self):
        """Walidacja zależności między polami (staż a źródło dochodu)."""
        cleaned_data = super().clean()

        income_type = cleaned_data.get("income_type")
        employment_years = cleaned_data.get("employment_years")

        IncomeType = LoanApplication.IncomeType
        requires_employment = {
            IncomeType.WORKING,
            IncomeType.COMMERCIAL_ASSOCIATE,
            IncomeType.STATE_SERVANT,
        }

        if income_type == IncomeType.PENSIONER and employment_years is not None:
            self.add_error("employment_years", "Pensioners should leave employment empty.")
        elif income_type in requires_employment and employment_years is None:
            self.add_error("employment_years", "Employment is required for this income type.")

        return cleaned_data
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class LoanApplication(models.Model):
    """Wniosek kredytowy: dane od klienta + wynik scoringu + status."""

    class Status(models.TextChoices):
        AUTO_APPROVED = "AUTO_APPROVED", "Auto approved"
        MANUAL_REVIEW = "MANUAL_REVIEW", "Manual review"
        AUTO_REJECTED = "AUTO_REJECTED", "Auto rejected"
        NOT_SCORED = "NOT_SCORED", "Not scored"

    class IncomeType(models.TextChoices):
        WORKING = "Working", "Working"
        COMMERCIAL_ASSOCIATE = "Commercial associate", "Commercial associate"
        PENSIONER = "Pensioner", "Pensioner"
        STATE_SERVANT = "State servant", "State servant"
        OTHER = "Other", "Other"

    class Education(models.TextChoices):
        SECONDARY = "Secondary / secondary special", "Secondary"
        HIGHER = "Higher education", "Higher"
        INCOMPLETE_HIGHER = "Incomplete higher", "Incomplete higher"
        LOWER_SECONDARY = "Lower secondary", "Lower secondary"
        ACADEMIC_DEGREE = "Academic degree", "Academic degree"

    income = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(1)])
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(1)])

    num_installments = models.PositiveSmallIntegerField(validators=[MinValueValidator(8), MaxValueValidator(46)])
    age_years = models.PositiveSmallIntegerField(validators=[MinValueValidator(20), MaxValueValidator(70)])

    employment_years = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])

    income_type = models.CharField(max_length=32, choices=IncomeType.choices)
    education = models.CharField(max_length=64, choices=Education.choices)

    ext_score_2 = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    ext_score_3 = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])

    probability_of_default = models.FloatField(null=True, blank=True)
    model_version = models.CharField(max_length=32, blank=True)

    status = models.CharField(max_length=20, default=Status.NOT_SCORED, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Application #{self.pk} ({self.status})"
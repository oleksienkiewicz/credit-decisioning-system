from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoanApplicationForm
from .models import LoanApplication
from .scoring_client import score_application

APPROVE_BELOW = 0.05
REJECT_ABOVE = 0.20


def decide_status(probability_of_default):
    """Zamienia PD na status wniosku według progów."""
    if probability_of_default < APPROVE_BELOW:
        return LoanApplication.Status.AUTO_APPROVED
    elif probability_of_default > REJECT_ABOVE:
        return LoanApplication.Status.AUTO_REJECTED
    else:
        return LoanApplication.Status.MANUAL_REVIEW 


def application_create(request):
    """Formularz nowego wniosku: GET pokazuje, POST zapisuje i ocenia."""
    if request.method == "POST":
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            result = score_application(application)

            if result is not None:
                application.probability_of_default = result["probability_of_default"]
                application.model_version = result["model_version"]
                application.status = decide_status(application.probability_of_default)
                application.save()

            return redirect("application_detail", pk=application.pk)
    else:
        form = LoanApplicationForm()

    return render(request, "applications/application_form.html", {"form": form})


def application_detail(request, pk):
    """Strona z danymi wniosku i decyzją."""
    application = get_object_or_404(LoanApplication, pk=pk)
    return render(request, "applications/application_detail.html", {"application": application})
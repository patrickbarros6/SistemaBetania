# accounts/views.py
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from core import services as core_services

def home(request):
    # raiz do site
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return redirect("accounts:login")

@login_required
def dashboard(request):
    ctx = {
        "kpis": core_services.get_kpis_for(request.user),
        "announcements": core_services.get_announcements(request.user),
        "today_events": core_services.get_today_events(request.user),
        "assignments": core_services.get_user_assignments(request.user),
        "pending": core_services.get_pending_actions(request.user),
    }
    return render(request, "accounts/dashboard.html", ctx)

# accounts/views.py
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

def home(request):
    # raiz do site
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return redirect("accounts:login")

@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Campaign, Invite
from .forms import RSVPForm

def rsvp_view(request, token):
    invite = get_object_or_404(Invite, token=token)
    if request.method == "POST":
        form = RSVPForm(request.POST)
        if form.is_valid():
            invite.responded = True
            invite.response = str(form.cleaned_data)
            invite.save()
            return redirect("campaigns:thanks")
    else:
        form = RSVPForm()
    return render(request, "campaigns/rsvp_form.html", {"form": form, "invite": invite})

def thanks_view(request):
    return render(request, "campaigns/thanks.html")

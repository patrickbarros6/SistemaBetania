
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
import csv, io

from .models import Event, Reservation
from .forms import EventForm, ReservationForm

def is_admin(u): return bool(u and u.is_authenticated and u.is_staff)

# ---- Painel/Admin ----
@login_required
@user_passes_test(is_admin)
def manage_list(request):
    qs = Event.objects.all()
    return render(request, "events/manage_list.html", {"events": qs})

@login_required
@user_passes_test(is_admin)
def manage_new(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento criado.")
            return redirect("events:manage_list")
    else:
        form = EventForm()
    return render(request, "events/manage_form.html", {"form": form, "title":"Novo evento"})

@login_required
@user_passes_test(is_admin)
def manage_edit(request, pk:int):
    e = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = EventForm(request.POST, instance=e)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento salvo.")
            return redirect("events:manage_list")
    else:
        form = EventForm(instance=e)
    return render(request, "events/manage_form.html", {"form": form, "title": f"Editar — {e.title}"})

@login_required
@user_passes_test(is_admin)
def manage_detail(request, pk:int):
    e = get_object_or_404(Event, pk=pk)
    rs = e.reservations.select_related("contact").all().order_by("name")
    return render(request, "events/manage_detail.html", {"e": e, "reservations": rs})

@login_required
@user_passes_test(is_admin)
def manage_checkin_toggle(request, pk:int, rid:int):
    e = get_object_or_404(Event, pk=pk)
    r = get_object_or_404(Reservation, pk=rid, event=e)
    if r.checked_in_at:
        r.checked_in_at = None
        messages.info(request, f"Check-in removido de {r.name}.")
    else:
        from django.utils import timezone
        r.checked_in_at = timezone.now()
        messages.success(request, f"Check-in marcado para {r.name}.")
    r.save(update_fields=["checked_in_at"])
    return redirect("events:manage_detail", pk=e.id)

@login_required
@user_passes_test(is_admin)
def manage_export_csv(request, pk:int):
    e = get_object_or_404(Event, pk=pk)
    rs = e.reservations.select_related("contact").all().order_by("name")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["name","phone","email","checked_in","created_at"])
    for r in rs:
        w.writerow([r.name, r.phone or "", r.email or "", "yes" if r.checked_in_at else "no", r.created_at.isoformat()])
    resp = HttpResponse(buf.getvalue(), content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="event_{e.id}_reservations.csv"'
    return resp

# ---- Público ----
def public_list(request):
    qs = Event.objects.filter(is_public=True).order_by("start_time")
    return render(request, "events/public_list.html", {"events": qs})

def public_rsvp(request, pk:int):
    e = get_object_or_404(Event, pk=pk, is_public=True)
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.event = e
            r.save()
            messages.success(request, "Inscrição registrada!")
            return redirect("events:public_rsvp", pk=e.id)
    else:
        form = ReservationForm()
    rs = e.reservations.select_related("contact").all().order_by("created_at")
    capacity_left = None
    if e.capacity is not None:
        capacity_left = max(e.capacity - rs.count(), 0)
    return render(request, "events/public_rsvp.html", {"e": e, "form": form, "reservations": rs, "capacity_left": capacity_left})

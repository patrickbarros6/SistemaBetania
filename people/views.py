
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Member, Unavailability
from .forms import MemberForm, UnavailabilityForm

def is_admin(u): return bool(u and u.is_authenticated and u.is_staff)

# ---- Members ----
@login_required
@user_passes_test(is_admin)
def members_list(request):
    q = request.GET.get("q","").strip()
    qs = Member.objects.all().order_by("name")
    if q:
        qs = qs.filter(name__icontains=q)
    return render(request, "people/members_list.html", {"members": qs, "q": q})

@login_required
@user_passes_test(is_admin)
def member_create(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Membro criado com sucesso.")
            return redirect("people:members_list")
    else:
        form = MemberForm()
    return render(request, "people/member_form.html", {"form": form, "title": "Novo membro"})

@login_required
@user_passes_test(is_admin)
def member_edit(request, pk:int):
    m = get_object_or_404(Member, pk=pk)
    if request.method == "POST":
        form = MemberForm(request.POST, instance=m)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados salvos.")
            return redirect("people:members_list")
    else:
        form = MemberForm(instance=m)
    return render(request, "people/member_form.html", {"form": form, "title": f"Editar — {m.name}"})

@login_required
@user_passes_test(is_admin)
def member_deactivate(request, pk:int):
    m = get_object_or_404(Member, pk=pk)
    m.active = False
    m.save(update_fields=["active"])
    messages.info(request, f"{m.name} desativado.")
    return redirect("people:members_list")

# ---- Unavailability ----
@login_required
@user_passes_test(is_admin)
def unavailability_list(request):
    qs = Unavailability.objects.select_related("member").all().order_by("-id")
    return render(request, "people/unavailability_list.html", {"items": qs})

@login_required
@user_passes_test(is_admin)
def unavailability_create(request):
    if request.method == "POST":
        form = UnavailabilityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Indisponibilidade registrada.")
            return redirect("people:unavailability_list")
    else:
        form = UnavailabilityForm()
    return render(request, "people/unavailability_form.html", {"form": form, "title": "Nova indisponibilidade"})

@login_required
@user_passes_test(is_admin)
def unavailability_edit(request, pk:int):
    u = get_object_or_404(Unavailability, pk=pk)
    if request.method == "POST":
        form = UnavailabilityForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            messages.success(request, "Alterações salvas.")
            return redirect("people:unavailability_list")
    else:
        form = UnavailabilityForm(instance=u)
    return render(request, "people/unavailability_form.html", {"form": form, "title": f"Editar — {u.member.name} {u.date}"})

@login_required
@user_passes_test(is_admin)
def unavailability_delete(request, pk:int):
    u = get_object_or_404(Unavailability, pk=pk)
    u.delete()
    messages.info(request, "Indisponibilidade removida.")
    return redirect("people:unavailability_list")

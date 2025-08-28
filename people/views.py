
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Member, Unavailability
from .forms import MemberForm, UnavailabilityForm
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
import csv, io

def is_admin(u): return bool(u and u.is_authenticated and u.is_staff)

# ---- Members ----
@login_required
@user_passes_test(is_admin)
def members_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    eligibility = request.GET.get("eligibility", "").strip()
    qs = Member.objects.all().order_by("name")
    if q:
        qs = qs.filter(name__icontains=q)
    if status in ("0", "1"):
        qs = qs.filter(active=(status == "1"))
    if eligibility in ("0", "1"):
        qs = qs.filter(kitchen_eligible=(eligibility == "1"))
    paginator = Paginator(qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    ctx = {
        "members": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "status": status,
        "eligibility": eligibility,
    }
    return render(request, "people/members.html", ctx)

@login_required
@user_passes_test(is_admin)
def member_form(request):
    mid = request.GET.get("id")
    inst = get_object_or_404(Member, pk=mid) if mid else None
    form = MemberForm(instance=inst)
    return render(request, "people/_member_form_fragment.html", {"form": form, "id": mid})

@login_required
@user_passes_test(is_admin)
def member_save(request):
    mid = request.POST.get("id")
    inst = get_object_or_404(Member, pk=mid) if mid else None
    form = MemberForm(request.POST, instance=inst)
    if form.is_valid():
        form.save()
        resp = HttpResponse(status=204)
        resp["HX-Redirect"] = "/people/members/"
        resp["HX-Trigger"] = "member:saved"
        return resp
    return render(request, "people/_member_form_fragment.html", {"form": form, "id": mid}, status=400)

@login_required
@user_passes_test(is_admin)
def member_toggle(request, pk:int):
    m = get_object_or_404(Member, pk=pk)
    m.active = not bool(m.active)
    m.save(update_fields=["active"])
    return render(request, "people/_member_row.html", {"m": m})

@login_required
@user_passes_test(is_admin)
def member_delete(request, pk:int):
    m = get_object_or_404(Member, pk=pk)
    m.delete()
    return HttpResponse("")

@login_required
@user_passes_test(is_admin)
def member_bulk_delete(request):
    ids = request.POST.getlist("ids")
    Member.objects.filter(id__in=ids).delete()
    return HttpResponse(status=204)

@login_required
@user_passes_test(is_admin)
def member_import_csv(request):
    f = request.FILES.get("import_csv") or request.FILES.get("file")
    if not f:
        return HttpResponse("Arquivo ausente", status=400)
    buf = io.TextIOWrapper(f.file, encoding="utf-8")
    reader = csv.DictReader(buf)
    created = 0
    for row in reader:
        name = (row.get("name") or row.get("Nome") or "").strip()
        phone = (row.get("phone") or row.get("Telefone") or "").strip()
        if not name:
            continue
        Member.objects.get_or_create(name=name, defaults={"phone": phone})
        created += 1
    messages.success(request, f"Importados {created} membros.")
    resp = HttpResponse(status=204)
    resp["HX-Redirect"] = "/people/members/"
    return resp

@login_required
@user_passes_test(is_admin)
def members_api(request):
    qs = Member.objects.all().order_by("name")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(name__icontains=q)
    data = [
        {
            "id": m.id,
            "name": m.name,
            "phone": m.phone,
            "active": bool(m.active),
            "kitchen_eligible": bool(m.kitchen_eligible),
        }
        for m in qs
    ]
    return JsonResponse({"results": data})

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


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import transaction
import json, io, csv, datetime, calendar
import pandas as pd

from .models import Schedule, Assignment
from .forms import GenerateScheduleForm, month_sundays
from .services.algorithm import generate_schedule, REQUIREMENTS
from core.models import Member

def is_admin(u): return bool(u and u.is_authenticated and u.is_staff)

@login_required
@user_passes_test(is_admin)
def schedule_list(request):
    qs = Schedule.objects.all().order_by("-year","-month","-id")
    return render(request, "schedules/list.html", {"schedules": qs})

@login_required
@user_passes_test(is_admin)
def schedule_detail(request, pk:int):
    s = get_object_or_404(Schedule, pk=pk)
    assignments = s.assignments.select_related("member").all()
    # pivot simples por data
    per_date = {}
    for a in assignments:
        per_date.setdefault(a.service_date, {"kitchen":[], "cleaning":[], "serving":[]})
        per_date[a.service_date][a.role].append(a.member.name)
    return render(request, "schedules/detail.html", {"s": s, "per_date": per_date, "req": REQUIREMENTS})

@login_required
@user_passes_test(is_admin)
def schedule_generate(request):
    if request.method == "POST":
        form = GenerateScheduleForm(request.POST)
        if form.is_valid():
            y = form.cleaned_data["year"]
            m = form.cleaned_data["month"]
            min_days_between = form.cleaned_data["min_days_between"]
            max_per_month = form.cleaned_data["max_per_month"]
            sundays = month_sundays(y, m)
            # pegar checkboxes enviados (name 'd_YYYY_MM_DD')
            selected = []
            for d in sundays:
                key = f"d_{d.strftime('%Y_%m_%d')}"
                if request.POST.get(key) == "on":
                    selected.append(d)
            # datas extras (CSV)
            extra = form.cleaned_data["extra_dates"].strip()
            if extra:
                for part in extra.split(","):
                    part = part.strip()
                    if not part: continue
                    try:
                        y2,m2,d2 = map(int, part.split("-"))
                        selected.append(datetime.date(y2,m2,d2))
                    except Exception:
                        return HttpResponseBadRequest(f"Data inválida: {part}")
            if not selected:
                return HttpResponseBadRequest("Selecione ao menos uma data.")
            # criar schedule e rodar
            with transaction.atomic():
                s = Schedule.objects.create(
                    year=y, month=m,
                    name=f"Escala {m:02d}/{y}",
                    selected_dates_json=json.dumps([d.isoformat() for d in selected]),
                    min_days_between=min_days_between,
                    max_per_month=max_per_month
                )
                created = generate_schedule(s, selected)
                Assignment.objects.bulk_create(created)
            return redirect("schedules:detail", pk=s.id)
    else:
        form = GenerateScheduleForm()
    # para o form, precisamos montar a lista de domingos do mês corrente do form (default)
    y = form["year"].value()
    m = form["month"].value()
    try:
        y = int(y); m = int(m)
    except Exception:
        today = datetime.date.today(); y = today.year; m = today.month
    sundays = month_sundays(y, m)
    # render com checkboxes
    return render(request, "schedules/generate.html", {"form": form, "sundays": sundays, "req": REQUIREMENTS})

@login_required
@user_passes_test(is_admin)
def schedule_export(request, pk:int):
    s = get_object_or_404(Schedule, pk=pk)
    fmt = request.GET.get("fmt","xlsx")
    # dataframe detalhado e pivot
    rows = []
    for a in s.assignments.select_related("member").all().order_by("service_date","role","member__name"):
        rows.append({"date": a.service_date.isoformat(), "role": a.role, "name": a.member.name})
    df = pd.DataFrame(rows)
    if df.empty:
        return HttpResponse("Sem dados.", content_type="text/plain")
    # pivot
    pivot = []
    for d, g in df.groupby("date"):
        row = {"date": d}
        for idx, n in enumerate(g[g["role"]=="kitchen"]["name"].tolist(), start=1):
            row[f"Kitchen{idx}"] = n
        for idx, n in enumerate(g[g["role"]=="cleaning"]["name"].tolist(), start=1):
            row[f"Cleaning{idx}"] = n
        for idx, n in enumerate(g[g["role"]=="serving"]["name"].tolist(), start=1):
            row[f"Serving{idx}"] = n
        pivot.append(row)
    piv = pd.DataFrame(pivot).sort_values("date")

    if fmt == "csv":
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        resp = HttpResponse(buf.getvalue(), content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="schedule_{s.year}_{s.month:02d}_detail.csv"'
        return resp
    else:
        import tempfile
        from pandas import ExcelWriter
        with pd.ExcelWriter(f"/mnt/data/schedule_{s.year}_{s.month:02d}.xlsx", engine="xlsxwriter") as writer:
            piv.to_excel(writer, sheet_name="Escala", index=False)
            df.to_excel(writer, sheet_name="Detalhe", index=False)
        with open(f"/mnt/data/schedule_{s.year}_{s.month:02d}.xlsx","rb") as f:
            data = f.read()
        resp = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp["Content-Disposition"] = f'attachment; filename="schedule_{s.year}_{s.month:02d}.xlsx"'
        return resp

@login_required
@user_passes_test(is_admin)
def schedule_report(request, pk:int):
    s = get_object_or_404(Schedule, pk=pk)
    # carga por pessoa neste schedule
    per_person = {}
    for a in s.assignments.select_related("member").all():
        p = per_person.setdefault(a.member_id, {"name": a.member.name, "total":0, "kitchen":0, "cleaning":0, "serving":0})
        p["total"] += 1; p[a.role] += 1
    # expectativa: total de posições / ativos
    total_positions = sum([
        REQUIREMENTS["kitchen_per_sunday"],
        REQUIREMENTS["cleaning_per_sunday"],
        REQUIREMENTS["serving_per_sunday"],
    ]) * len(set([a.service_date for a in s.assignments.all()]))
    active_count = Member.objects.filter(active=True).count() or 1
    expected = total_positions / active_count
    few, many = [], []
    for v in per_person.values():
        ratio = v["total"] / expected if expected else 0
        v["ratio"] = round(ratio, 2)
        if ratio < 0.5: few.append(v)
        if ratio > 1.5: many.append(v)
    return render(request, "schedules/report.html", {
        "s": s, "per_person": sorted(per_person.values(), key=lambda x:(-x["total"], x["name"])),
        "expected": round(expected,2),
        "alerts_few": few,
        "alerts_many": many,
    })

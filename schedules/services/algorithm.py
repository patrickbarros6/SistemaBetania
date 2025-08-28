
import random, json, datetime
from collections import defaultdict
from typing import List, Dict, Set
from django.db.models import Q
from core.models import Member, Unavailability
from schedules.models import Schedule, Assignment

REQUIREMENTS = {
    "kitchen_per_sunday": 2,
    "cleaning_per_sunday": 4,
    "serving_per_sunday": 2,
}
RANDOM_SEED = 42

def build_stats(prior_assignments):
    stats = defaultdict(lambda: {"total":0,"kitchen":0,"cleaning":0,"serving":0,"last_date":None,"last_role":None})
    for a in prior_assignments:
        s = stats[a.member_id]
        s["total"] += 1
        s[a.role] += 1
        if (s["last_date"] is None) or (a.service_date > s["last_date"]):
            s["last_date"] = a.service_date
            s["last_role"] = a.role
    return stats

def score_person(member_id, role, stats, service_date, recent_days_window=28):
    s = stats.get(member_id, {"total":0,"kitchen":0,"cleaning":0,"serving":0,"last_date":None,"last_role":None})
    base = s["total"]
    role_bias = 0.2 * s.get(role, 0)
    recent_pen = 0.0
    if s["last_date"] is not None:
        delta = (service_date - s["last_date"]).days
        if 0 <= delta <= recent_days_window:
            recent_pen = 2.0 * (1 - delta / recent_days_window)
    same_role_pen = 0.5 if s["last_role"] == role else 0.0
    return base + role_bias + recent_pen + same_role_pen

def normalize_dates(selected_dates: List[datetime.date]) -> List[datetime.date]:
    # ordena e remove duplicadas
    uniq = sorted(set(selected_dates))
    return uniq

def generate_schedule(schedule: Schedule, selected_dates: List[datetime.date]) -> List[Assignment]:
    dates = normalize_dates(selected_dates)
    # universo
    active_members = list(Member.objects.filter(active=True).order_by("name"))
    kitchen_ids = set(Member.objects.filter(active=True, kitchen_eligible=True).values_list("id", flat=True))
    service_ids = set(m.id for m in active_members)  # todos podem limpeza/servir
    # indisponibilidades
    unavail = Unavailability.objects.filter(date__in=[d.isoformat() for d in dates])
    unavail_map: Dict[tuple, Set[int]] = defaultdict(set)  # (date) -> member_ids indisponíveis
    for u in unavail:
        try:
            y,m,d = map(int, u.date.split("-"))
            dt = datetime.date(y,m,d)
            unavail_map[dt].add(u.member_id)
        except Exception:
            continue
    # estatísticas (olha assignments anteriores)
    prior = Assignment.objects.filter(service_date__lt=min(dates)).order_by("service_date")
    stats = build_stats(prior)

    # limites por pessoa no mês
    month_key = (schedule.year, schedule.month)
    month_counts = defaultdict(int)

    # helper para pegar candidatos
    def eligible(pool_ids:Set[int], role:str, d:datetime.date, picked_today:Set[int]):
        ids = []
        for mid in pool_ids:
            if mid in picked_today: continue
            if mid in unavail_map.get(d, set()): continue
            if month_counts[mid] >= schedule.max_per_month: continue
            last_date = stats.get(mid, {}).get("last_date")
            if last_date is not None and (d - last_date).days < schedule.min_days_between:
                continue
            ids.append(mid)
        return ids

    created = []
    for d in dates:
        picked_today:set[int] = set()
        # cozinha
        kuch_pool = eligible(kitchen_ids, "kitchen", d, picked_today)
        rnd = random.Random(RANDOM_SEED + hash(str(d)) + hash("kitchen"))
        rnd.shuffle(kuch_pool)
        kuch_scored = sorted([(score_person(mid,"kitchen",stats,d), mid) for mid in kuch_pool], key=lambda x:x[0])
        kuch_pick = [mid for _, mid in kuch_scored[:REQUIREMENTS["kitchen_per_sunday"]]]
        for mid in kuch_pick:
            a = Assignment(schedule=schedule, service_date=d, role="kitchen", member_id=mid)
            created.append(a)
            picked_today.add(mid)
            month_counts[mid] += 1
            s = stats.setdefault(mid, {"total":0,"kitchen":0,"cleaning":0,"serving":0,"last_date":None,"last_role":None})
            s["total"] += 1; s["kitchen"] += 1; s["last_date"] = d; s["last_role"] = "kitchen"

        # limpeza
        clean_pool = eligible(service_ids, "cleaning", d, picked_today)
        rnd = random.Random(RANDOM_SEED + hash(str(d)) + hash("cleaning"))
        rnd.shuffle(clean_pool)
        clean_scored = sorted([(score_person(mid,"cleaning",stats,d), mid) for mid in clean_pool], key=lambda x:x[0])
        clean_pick = [mid for _, mid in clean_scored[:REQUIREMENTS["cleaning_per_sunday"]]]
        for mid in clean_pick:
            a = Assignment(schedule=schedule, service_date=d, role="cleaning", member_id=mid)
            created.append(a)
            picked_today.add(mid)
            month_counts[mid] += 1
            s = stats.setdefault(mid, {"total":0,"kitchen":0,"cleaning":0,"serving":0,"last_date":None,"last_role":None})
            s["total"] += 1; s["cleaning"] += 1; s["last_date"] = d; s["last_role"] = "cleaning"

        # servir
        serv_pool = eligible(service_ids - picked_today, "serving", d, picked_today)
        rnd = random.Random(RANDOM_SEED + hash(str(d)) + hash("serving"))
        rnd.shuffle(serv_pool)
        serv_scored = sorted([(score_person(mid,"serving",stats,d), mid) for mid in serv_pool], key=lambda x:x[0])
        serv_pick = [mid for _, mid in serv_scored[:REQUIREMENTS["serving_per_sunday"]]]
        for mid in serv_pick:
            a = Assignment(schedule=schedule, service_date=d, role="serving", member_id=mid)
            created.append(a)
            picked_today.add(mid)
            month_counts[mid] += 1
            s = stats.setdefault(mid, {"total":0,"kitchen":0,"cleaning":0,"serving":0,"last_date":None,"last_role":None})
            s["total"] += 1; s["serving"] += 1; s["last_date"] = d; s["last_role"] = "serving"

    return created

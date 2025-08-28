from datetime import timedelta
from django.utils import timezone
from django.db.models import Q


def _safe_imports():
    try:
        from events.models import Event
    except Exception:
        Event = None
    try:
        from schedules.models import Assignment
    except Exception:
        Assignment = None
    try:
        from core.models import Member, SurveyCampaign, SurveyInvite
    except Exception:
        Member = SurveyCampaign = SurveyInvite = None
    try:
        from accounts.models import Profile
    except Exception:
        Profile = None
    return Event, Assignment, Member, SurveyCampaign, SurveyInvite, Profile


def get_today_events(user, limit: int = 5):
    Event, _, _, _, _, _ = _safe_imports()
    if not Event:
        return []
    now = timezone.localtime()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    try:
        qs = (
            Event.objects.filter(start_time__gte=start, start_time__lt=end)
            .order_by("start_time")
        )
        items = []
        for e in qs[:limit]:
            items.append(
                {
                    "title": e.title,
                    "start": timezone.localtime(e.start_time).strftime("%Y-%m-%d %H:%M"),
                    "location": e.location or "",
                }
            )
        return items
    except Exception:
        return []


def _member_for_user(user):
    _, _, Member, _, _, Profile = _safe_imports()
    if not Member or not user or not user.is_authenticated:
        return None
    # 1) perfil explícito
    try:
        if Profile and hasattr(user, "profile") and user.profile and user.profile.member:
            return user.profile.member
    except Exception:
        pass
    full = (user.get_full_name() or "").strip()
    uname = (user.username or "").strip()
    try:
        if full:
            m = Member.objects.filter(name__iexact=full).first()
            if m:
                return m
        if uname:
            return Member.objects.filter(name__iexact=uname).first()
    except Exception:
        return None
    return None


def get_user_assignments(user, limit: int = 5):
    _, Assignment, _, _, _, _ = _safe_imports()
    if not Assignment:
        return []
    try:
        today = timezone.localtime().date()
        qs = Assignment.objects.select_related("member").filter(service_date__gte=today)
        m = _member_for_user(user)
        if m and not user.is_staff:
            qs = qs.filter(member=m)
        qs = qs.order_by("service_date")[:limit]
        return [
            {
                "date": a.service_date.isoformat(),
                "role": a.get_role_display(),
                "team": "Serviço",
                "status": "Confirmado" if a.service_date <= today else "Pendente",
            }
            for a in qs
        ]
    except Exception:
        return []


def get_pending_actions(user):
    _, _, _, SurveyCampaign, SurveyInvite, _ = _safe_imports()
    data = {"confirmations": 0, "swaps": 0, "approvals": 0}
    if not (SurveyCampaign and SurveyInvite):
        return data
    try:
        camp = SurveyCampaign.objects.order_by("-year", "-month", "-id").first()
        if not camp:
            return data
        pending = SurveyInvite.objects.filter(campaign=camp).filter(
            Q(responded_at__isnull=True) | Q(responded_at__exact="")
        ).count()
        data["confirmations"] = pending
        return data
    except Exception:
        return data


def get_kpis_for(user):
    Event, Assignment, Member, _, _, _ = _safe_imports()
    kpis = []
    try:
        active_members = Member.objects.filter(active=True).count() if Member else 0
    except Exception:
        active_members = 0
    try:
        now = timezone.localtime()
        soon = now + timedelta(days=7)
        events_week = (
            Event.objects.filter(start_time__gte=now, start_time__lt=soon).count()
            if Event
            else 0
        )
    except Exception:
        events_week = 0
    try:
        today = timezone.localtime().date()
        month_start = today.replace(day=1)
        if today.month == 12:
            next_month_start = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month_start = today.replace(month=today.month + 1, day=1)
        assignments_month = (
            Assignment.objects.filter(
                service_date__gte=month_start, service_date__lt=next_month_start
            ).count()
            if Assignment
            else 0
        )
    except Exception:
        assignments_month = 0

    kpis.append({"label": "Pessoas ativas", "value": active_members})
    kpis.append({"label": "Eventos (7 dias)", "value": events_week})
    kpis.append({"label": "Escalas no mês", "value": assignments_month})
    return kpis


def get_announcements(user, limit=3):
    return [
        {"title": "Bem-vindo!", "text": "Use o menu para acessar os módulos."},
    ][:limit]

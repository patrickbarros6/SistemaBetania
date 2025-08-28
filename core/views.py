from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Q
from .models import Member, MemberPref, Unavailability, SurveyInvite, SurveyCampaign
from .serializers import MemberSerializer, MemberPrefSerializer, UnavailabilitySerializer, CampaignSerializer, InviteSerializer
from .utils import detect_lang_for_member, month_name, format_dates_list, render_message
import calendar, datetime, uuid
from twilio.rest import Client
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from . import services
def twilio_client():
    sid = settings.TWILIO_ACCOUNT_SID
    tok = settings.TWILIO_AUTH_TOKEN
    if not sid or not tok:
        raise RuntimeError("Twilio não configurado. Defina TWILIO_ACCOUNT_SID e TWILIO_AUTH_TOKEN.")
    return Client(sid, tok)
def normalize_whatsapp(phone: str) -> str:
    phone = (phone or "").strip()
    if not phone: return ""
    if phone.startswith("whatsapp:"): return phone
    if phone.startswith("+"): return f"whatsapp:{phone}"
    digits = "".join(ch for ch in phone if ch.isdigit())
    if not digits: return ""
    return f"whatsapp:+{digits}"
def get_sundays(year:int, month:int):
    cal = calendar.Calendar(firstweekday=6)
    return [d for w in cal.monthdatescalendar(year, month) for d in w if d.month == month and d.weekday() == 6]
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all().order_by("name")
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.request.method in ("POST","PUT","PATCH","DELETE"):
            return [IsAdmin()]
        return super().get_permissions()
class MemberPrefViewSet(viewsets.ModelViewSet):
    queryset = MemberPref.objects.select_related("member").all().order_by("member__name")
    serializer_class = MemberPrefSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.request.method in ("POST","PUT","PATCH","DELETE"):
            return [IsAdmin()]
        return super().get_permissions()
class UnavailabilityViewSet(viewsets.ModelViewSet):
    queryset = Unavailability.objects.all()
    serializer_class = UnavailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = SurveyCampaign.objects.all().order_by("-year","-month")
    serializer_class = CampaignSerializer
    permission_classes = [IsAdmin]
    def create(self, request, *args, **kwargs):
        year = int(request.data.get("year"))
        month = int(request.data.get("month"))
        template = request.data.get("message_template") or None
        camp = SurveyCampaign.objects.create(year=year, month=month, created_at=datetime.datetime.utcnow().isoformat(), message_template=template)
        members = Member.objects.filter(active=True).exclude(Q(phone__isnull=True) | Q(phone__exact="")).order_by("name")
        created = 0
        for m in members:
            if SurveyInvite.objects.filter(campaign=camp, member=m).exists(): continue
            SurveyInvite.objects.create(campaign=camp, member=m, token=uuid.uuid4().hex, sent_at=None)
            created += 1
        ser = self.get_serializer(camp)
        return Response({"campaign": ser.data, "invites_created": created}, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=["get"], permission_classes=[IsAdmin])
    def invites(self, request, pk=None):
        camp = self.get_object()
        qs = SurveyInvite.objects.filter(campaign=camp).select_related("member").order_by("id")
        ser = InviteSerializer(qs, many=True)
        return Response(ser.data)
    @action(detail=True, methods=["get"], permission_classes=[IsAdmin])
    def stats(self, request, pk=None):
        camp = self.get_object()
        total = SurveyInvite.objects.filter(campaign=camp).count()
        responded = SurveyInvite.objects.filter(campaign=camp).exclude(responded_at__isnull=True).exclude(responded_at__exact="").count()
        available_all = SurveyInvite.objects.filter(campaign=camp, available_all=True).count()
        return Response({"campaign_id": camp.id, "year": camp.year, "month": camp.month, "total_invites": total, "responded": responded, "available_all": available_all})
    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def send(self, request, pk=None):
        camp = self.get_object()
        client = twilio_client()
        base_url = getattr(settings, "PUBLIC_BASE_URL", "http://localhost:8001")
        from_num = getattr(settings, "TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        church_name = getattr(settings, "CHURCH_NAME", "Igreja Betânia")
        sundays = get_sundays(camp.year, camp.month)
        sent=0; skipped=0; errors=0
        for inv in SurveyInvite.objects.filter(campaign=camp).select_related("member"):
            if inv.sent_at: skipped += 1; continue
            member = inv.member
            to = normalize_whatsapp(member.phone or "")
            if not to: skipped += 1; continue
            if not inv.token: inv.token = uuid.uuid4().hex
            lang = detect_lang_for_member(member)
            ctx = {
                "name": member.name,
                "church_name": church_name,
                "year": camp.year,
                "month_name": month_name(lang, camp.month),
                "dates_list": format_dates_list(sundays, lang),
                "rsvp_link": f"{base_url}/rsvp/{inv.token}",
            }
            try:
                body = render_message("invite", lang, ctx, camp.message_template)
                client.messages.create(from_=from_num, to=to, body=body)
                inv.sent_at = datetime.datetime.utcnow().isoformat()
                inv.save(update_fields=["token","sent_at"])
                sent += 1
            except Exception:
                errors += 1
        return Response({"campaign_id": camp.id, "sent": sent, "skipped": skipped, "errors": errors})
    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def remind(self, request, pk=None):
        camp = self.get_object()
        client = twilio_client()
        base_url = getattr(settings, "PUBLIC_BASE_URL", "http://localhost:8001")
        from_num = getattr(settings, "TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        church_name = getattr(settings, "CHURCH_NAME", "Igreja Betânia")
        max_days = int(getattr(settings, "REMINDER_MAX_DAYS", 7))
        today = datetime.date.today()
        reminded=0; skipped=0; errors=0
        invites = SurveyInvite.objects.filter(campaign=camp).filter(Q(responded_at__isnull=True) | Q(responded_at__exact="")).select_related("member")
        for inv in invites:
            if inv.reminders_sent is not None and inv.reminders_sent >= max_days:
                skipped += 1; continue
            if inv.last_reminder_at:
                try:
                    last = datetime.datetime.fromisoformat(inv.last_reminder_at).date()
                    if last == today:
                        skipped += 1; continue
                except Exception:
                    pass
            member = inv.member
            to = normalize_whatsapp(member.phone or "")
            if not to: skipped += 1; continue
            lang = detect_lang_for_member(member)
            ctx = {
                "name": member.name,
                "church_name": church_name,
                "year": camp.year,
                "month_name": month_name(lang, camp.month),
                "dates_list": "",
                "rsvp_link": f"{base_url}/rsvp/{inv.token}",
            }
            try:
                body = render_message("reminder", lang, ctx, camp.message_template)
                client.messages.create(from_=from_num, to=to, body=body)
                inv.reminders_sent = (inv.reminders_sent or 0) + 1
                inv.last_reminder_at = datetime.datetime.utcnow().isoformat()
                inv.save(update_fields=["reminders_sent","last_reminder_at"])
                reminded += 1
            except Exception:
                errors += 1
        return Response({"campaign_id": camp.id, "reminded": reminded, "skipped": skipped, "errors": errors})
class InviteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InviteSerializer
    permission_classes = [IsAdmin]
    def get_queryset(self):
        qs = SurveyInvite.objects.select_related("member","campaign").all().order_by("-id")
        campaign = self.request.query_params.get("campaign")
        responded = self.request.query_params.get("responded")
        if campaign: qs = qs.filter(campaign_id=campaign)
        if responded == "1":
            qs = qs.exclude(responded_at__isnull=True).exclude(responded_at__exact="")
        elif responded == "0":
            qs = qs.filter(Q(responded_at__isnull=True) | Q(responded_at__exact=""))
        return qs
@api_view(["GET"])
def me(request):
    role = "admin" if request.user.is_staff else "member"
    return Response({"id": request.user.id, "username": request.user.username, "role": role, "name": request.user.get_full_name() or request.user.username})
def rsvp_home(request): return render(request, "home.html")
def rsvp_form(request, token: str):
    invite = get_object_or_404(SurveyInvite, token=token)
    if invite.responded_at:
        return render(request, "thanks.html", {"already": True})
    camp = invite.campaign
    sundays = get_sundays(camp.year, camp.month)
    if request.method == "POST":
        if request.POST.get("available_all") == "on":
            invite.available_all = True
            invite.responded_at = datetime.datetime.utcnow().isoformat()
            invite.save(update_fields=["available_all","responded_at"])
            return redirect("thanks")
        else:
            dates = request.POST.getlist("unavail_dates")
            for ds in dates:
                note = request.POST.get(f"reason_{ds}", "")
                Unavailability.objects.create(member=invite.member, date=ds, role=None, note=note)
            invite.responded_at = datetime.datetime.utcnow().isoformat()
            invite.save(update_fields=["responded_at"])
            return redirect("thanks")
    return render(request, "rsvp.html", {"token": token, "name": invite.member.name, "year": camp.year, "month": camp.month, "sundays": sundays})
def thanks(request): return render(request, "thanks.html", {"already": False})



@login_required
def home(request):
    user = request.user

    # Exemplo simples de papéis (ajuste para o seu RBAC real)
    groups = set(g.name.lower() for g in user.groups.all())
    role = "voluntario"
    if "pastor" in groups or user.is_superuser:
        role = "pastor"
    elif "lider" in groups:
        role = "lider"
    elif "secretaria" in groups or "crm" in groups:
        role = "secretaria"

    context = {
        "role": role,
        "today_events": services.get_today_events(user),
        "my_assignments": services.get_user_assignments(user),
        "pending": services.get_pending_actions(user),
        "kpis": services.get_kpis_for(user),
        "announcements": services.get_announcements(user),
    }
    return render(request, "core/home.html", context)

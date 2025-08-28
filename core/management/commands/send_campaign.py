from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import SurveyCampaign, SurveyInvite
from core.utils import detect_lang_for_member, month_name, format_dates_list, render_message
from twilio.rest import Client
from datetime import datetime
import calendar
def get_sundays(year:int, month:int):
    cal = calendar.Calendar(firstweekday=6)
    return [d for w in cal.monthdatescalendar(year, month) for d in w if d.month == month and d.weekday() == 6]
def normalize_whatsapp(phone: str) -> str:
    phone = (phone or "").strip()
    if not phone: return ""
    if phone.startswith("whatsapp:"): return phone
    if phone.startswith("+"): return f"whatsapp:{phone}"
    digits = "".join(ch for ch in phone if ch.isdigit())
    if not digits: return ""
    return f"whatsapp:+{digits}"
class Command(BaseCommand):
    help = "Envia mensagens iniciais da campanha via Twilio (apenas para convites sem sent_at)."
    def add_arguments(self, parser):
        parser.add_argument("--id", type=int, required=True, help="ID da campanha")
        parser.add_argument("--force", action="store_true", help="Reenviar mesmo se já enviado (força envio)")
    def handle(self, *args, **opts):
        camp_id = opts["id"]; force = opts["force"]
        try:
            camp = SurveyCampaign.objects.get(id=camp_id)
        except SurveyCampaign.DoesNotExist:
            raise CommandError("Campanha não encontrada.")
        sid = settings.TWILIO_ACCOUNT_SID; tok = settings.TWILIO_AUTH_TOKEN
        if not sid or not tok:
            raise CommandError("Twilio não configurado (TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN).")
        client = Client(sid, tok)
        from_num = settings.TWILIO_WHATSAPP_FROM
        base_url = settings.PUBLIC_BASE_URL
        church = getattr(settings, "CHURCH_NAME", "Igreja Betânia")
        sundays = get_sundays(camp.year, camp.month)
        sent = 0; skipped = 0; errors = 0
        for inv in SurveyInvite.objects.select_related("member").filter(campaign=camp).order_by("id"):
            if inv.sent_at and not force:
                skipped += 1; continue
            to = normalize_whatsapp(inv.member.phone)
            if not to:
                skipped += 1; continue
            if not inv.token:
                import uuid
                inv.token = uuid.uuid4().hex
            lang = detect_lang_for_member(inv.member)
            ctx = {
                "name": inv.member.name,
                "church_name": church,
                "year": camp.year,
                "month_name": month_name(lang, camp.month),
                "dates_list": format_dates_list(sundays, lang),
                "rsvp_link": f"{base_url}/rsvp/{inv.token}",
            }
            try:
                body = render_message("invite", lang, ctx, camp.message_template)
                client.messages.create(from_=from_num, to=to, body=body)
                inv.sent_at = datetime.utcnow().isoformat()
                inv.save(update_fields=["token","sent_at"])
                sent += 1
            except Exception as e:
                errors += 1
        self.stdout.write(self.style.SUCCESS(f"Campanha {camp.id}: enviados={sent}, pulados={skipped}, erros={errors}"))

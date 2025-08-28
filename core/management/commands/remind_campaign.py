from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import SurveyCampaign, SurveyInvite
from core.utils import detect_lang_for_member, month_name, render_message
from twilio.rest import Client
from datetime import datetime, date
def normalize_whatsapp(phone: str) -> str:
    phone = (phone or "").strip()
    if not phone: return ""
    if phone.startswith("whatsapp:"): return phone
    if phone.startswith("+"): return f"whatsapp:{phone}"
    digits = "".join(ch for ch in phone if ch.isdigit())
    if not digits: return ""
    return f"whatsapp:+{digits}"
class Command(BaseCommand):
    help = "Envia lembretes da campanha via Twilio para quem não respondeu (máx. REMINDER_MAX_DAYS, 1 por dia)."
    def add_arguments(self, parser):
        parser.add_argument("--id", type=int, required=True, help="ID da campanha")
    def handle(self, *args, **opts):
        camp_id = opts["id"]
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
        max_days = int(getattr(settings, "REMINDER_MAX_DAYS", 7))
        church = getattr(settings, "CHURCH_NAME", "Igreja Betânia")
        today = date.today()
        reminded = 0; skipped = 0; errors = 0
        invites = SurveyInvite.objects.select_related("member").filter(campaign=camp).filter(responded_at__isnull=True) | SurveyInvite.objects.select_related("member").filter(campaign=camp, responded_at__exact="")
        for inv in invites:
            if inv.reminders_sent and inv.reminders_sent >= max_days:
                skipped += 1; continue
            if inv.last_reminder_at:
                try:
                    last = datetime.fromisoformat(inv.last_reminder_at).date()
                    if last == today:
                        skipped += 1; continue
                except Exception:
                    pass
            to = normalize_whatsapp(inv.member.phone)
            if not to:
                skipped += 1; continue
            lang = detect_lang_for_member(inv.member)
            ctx = {
                "name": inv.member.name,
                "church_name": church,
                "year": camp.year,
                "month_name": month_name(lang, camp.month),
                "dates_list": "",
                "rsvp_link": f"{base_url}/rsvp/{inv.token}",
            }
            try:
                body = render_message("reminder", lang, ctx, camp.message_template)
                client.messages.create(from_=from_num, to=to, body=body)
                inv.reminders_sent = (inv.reminders_sent or 0) + 1
                inv.last_reminder_at = datetime.utcnow().isoformat()
                inv.save(update_fields=["reminders_sent","last_reminder_at"])
                reminded += 1
            except Exception as e:
                errors += 1
        self.stdout.write(self.style.SUCCESS(f"Campanha {camp.id}: lembretes={reminded}, pulados={skipped}, erros={errors}"))

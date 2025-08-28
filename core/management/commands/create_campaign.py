from django.core.management.base import BaseCommand, CommandError
from core.models import SurveyCampaign, SurveyInvite, Member
from datetime import datetime
import uuid
class Command(BaseCommand):
    help = "Cria campanha (year, month) e gera convites para membros ativos com telefone."
    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, required=True)
        parser.add_argument("--month", type=int, required=True)
        parser.add_argument("--message", type=str, default=None, help="Template (pode ser JSON com pt/es)")
    def handle(self, *args, **opts):
        year = opts["year"]; month = opts["month"]; msg = opts["message"]
        if not (1 <= month <= 12): raise CommandError("Mês inválido (1-12).")
        camp = SurveyCampaign.objects.create(year=year, month=month, created_at=datetime.utcnow().isoformat(), message_template=msg)
        members = Member.objects.filter(active=True).exclude(phone__isnull=True).exclude(phone__exact="")
        created = 0
        for m in members:
            if SurveyInvite.objects.filter(campaign=camp, member=m).exists(): continue
            SurveyInvite.objects.create(campaign=camp, member=m, token=uuid.uuid4().hex, sent_at=None)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Campanha {camp.id} criada ({month:02d}/{year}). Convites: {created}"))

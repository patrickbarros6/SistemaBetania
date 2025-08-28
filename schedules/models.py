
from django.db import models
from django.utils import timezone
from core.models import Member

class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    month = models.IntegerField()
    name = models.CharField(max_length=200, default="", blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    selected_dates_json = models.TextField(blank=True, null=True)  # string JSON de datas selecionadas
    min_days_between = models.IntegerField(default=21)
    max_per_month = models.IntegerField(default=1)  # 1 função/mês/pessoa
    notes = models.TextField(blank=True, null=True)
    class Meta:
        ordering = ["-year", "-month", "-id"]
    def __str__(self): return self.name or f"Escala {self.month:02d}/{self.year}"

class Assignment(models.Model):
    ROLE_CHOICES = (("kitchen","cozinha"),("cleaning","limpeza"),("serving","servir"))
    id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="assignments")
    service_date = models.DateField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    class Meta:
        unique_together = (("service_date","role","member","schedule"),)
        indexes = [models.Index(fields=["service_date","role"]), models.Index(fields=["member"])]
        ordering = ["service_date","role","member__name"]
    def __str__(self): return f"{self.service_date} · {self.get_role_display()} · {self.member.name}"

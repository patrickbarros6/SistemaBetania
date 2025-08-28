from django.db import models
from django.utils import timezone
import uuid

class Campaign(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Campanha {self.month}/{self.year}"

class Invite(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="invites")
    member_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    responded = models.BooleanField(default=False)
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Convite {self.member_name} ({self.campaign})"

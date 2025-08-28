
from django.db import models
from django.utils import timezone
from crm.models import Contact

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)  # None = ilimitado
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)  # aparece na lista pública

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self): return f"{self.title} ({self.start_time:%d/%m %H:%M})"

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="reservations")
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)      # fallback se não houver contato
    phone = models.CharField(max_length=40, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    checked_in_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = (("event","contact"),)
        ordering = ["name"]

    def __str__(self): return f"{self.name} @ {self.event.title}"

    @property
    def checked_in(self): return bool(self.checked_in_at)

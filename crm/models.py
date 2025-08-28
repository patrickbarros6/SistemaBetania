
from django.db import models
from django.utils import timezone

class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=40, blank=True, null=True)  # +55... / +54...
    email = models.EmailField(blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True, help_text="Separadas por vírgula")
    opt_in = models.BooleanField(default=True, help_text="Autorizou comunicações")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self): return self.name

class Note(models.Model):
    id = models.AutoField(primary_key=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="notes")
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return f"Nota {self.created_at:%Y-%m-%d} - {self.contact.name}"

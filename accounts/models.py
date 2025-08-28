from django.db import models
from django.contrib.auth.models import User
from core.models import Member


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_profiles")

    class Meta:
        db_table = "user_profiles"

    def __str__(self) -> str:
        return f"Profile({self.user.username})"


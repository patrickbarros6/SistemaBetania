from django.db import models
class Member(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=32, blank=True, null=True)
    kitchen_eligible = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    class Meta:
        db_table = "members"
        managed = False
    def __str__(self): return self.name
class MemberPref(models.Model):
    LANG_CHOICES = (("pt","Português"),("es","Español"))
    member = models.OneToOneField(Member, on_delete=models.CASCADE, primary_key=True, db_column="member_id")
    language = models.CharField(max_length=2, choices=LANG_CHOICES, default="pt")
    class Meta:
        db_table = "member_prefs"
        managed = True
class SurveyCampaign(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    month = models.IntegerField()
    created_at = models.CharField(max_length=40, blank=True, null=True)
    message_template = models.TextField(blank=True, null=True)
    class Meta:
        db_table = "survey_campaigns"
        managed = False
    def __str__(self): return f"Campanha {self.month:02d}/{self.year}"
class SurveyInvite(models.Model):
    id = models.AutoField(primary_key=True)
    campaign = models.ForeignKey(SurveyCampaign, on_delete=models.DO_NOTHING, db_column="campaign_id")
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, db_column="member_id")
    token = models.CharField(max_length=64, unique=True)
    sent_at = models.CharField(max_length=40, blank=True, null=True)
    responded_at = models.CharField(max_length=40, blank=True, null=True)
    reminders_sent = models.IntegerField(default=0)
    last_reminder_at = models.CharField(max_length=40, blank=True, null=True)
    available_all = models.BooleanField(default=False)
    class Meta:
        db_table = "survey_invites"
        managed = False
class Unavailability(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, db_column="member_id")
    date = models.CharField(max_length=10)
    role = models.CharField(max_length=20, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    class Meta:
        db_table = "unavailability"
        managed = False

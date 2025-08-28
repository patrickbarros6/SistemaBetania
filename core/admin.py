from django.contrib import admin
from .models import Member, MemberPref, SurveyCampaign, SurveyInvite, Unavailability
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id","name","phone","kitchen_eligible","active")
    list_filter = ("active","kitchen_eligible")
    search_fields = ("name","phone")
@admin.register(MemberPref)
class MemberPrefAdmin(admin.ModelAdmin):
    list_display = ("member","language")
    list_filter = ("language",)
    search_fields = ("member__name",)
@admin.register(SurveyCampaign)
class SurveyCampaignAdmin(admin.ModelAdmin):
    list_display = ("id","year","month","created_at")
@admin.register(SurveyInvite)
class SurveyInviteAdmin(admin.ModelAdmin):
    list_display = ("id","campaign","member","token","sent_at","responded_at","reminders_sent","available_all")
    list_filter = ("available_all",)
@admin.register(Unavailability)
class UnavailabilityAdmin(admin.ModelAdmin):
    list_display = ("id","member","date","role","note")
    list_filter = ("role",)
    search_fields = ("member__name","note")

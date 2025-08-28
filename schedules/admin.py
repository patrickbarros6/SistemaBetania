
from django.contrib import admin
from .models import Schedule, Assignment

class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("id","name","year","month","created_at","min_days_between","max_per_month")
    list_filter = ("year","month")
    inlines = [AssignmentInline]

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("id","schedule","service_date","role","member")
    list_filter = ("role","service_date")
    search_fields = ("member__name",)

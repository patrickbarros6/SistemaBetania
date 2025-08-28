
from django.urls import path
from . import views

app_name = "schedules"
urlpatterns = [
    path("", views.schedule_list, name="list"),
    path("generate/", views.schedule_generate, name="generate"),
    path("<int:pk>/", views.schedule_detail, name="detail"),
    path("<int:pk>/export/", views.schedule_export, name="export"),
    path("<int:pk>/report/", views.schedule_report, name="report"),
]

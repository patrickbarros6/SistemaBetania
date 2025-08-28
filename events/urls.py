
from django.urls import path, include
from rest_framework import routers
from .api import EventViewSet, ReservationViewSet
from . import views

app_name = "events"
router = routers.DefaultRouter()
router.register(r"events", EventViewSet, basename="events-api")
router.register(r"reservations", ReservationViewSet, basename="reservations-api")

urlpatterns = [
    # Admin/painel
    path("manage/", views.manage_list, name="manage_list"),
    path("manage/new/", views.manage_new, name="manage_new"),
    path("manage/<int:pk>/", views.manage_detail, name="manage_detail"),
    path("manage/<int:pk>/edit/", views.manage_edit, name="manage_edit"),
    path("manage/<int:pk>/export/", views.manage_export_csv, name="manage_export"),
    path("manage/<int:pk>/checkin/<int:rid>/", views.manage_checkin_toggle, name="manage_checkin_toggle"),

    # Público
    path("public/", views.public_list, name="public_list"),
    path("public/<int:pk>/", views.public_rsvp, name="public_rsvp"),

    # APIs
    path("api/", include(router.urls)),
]

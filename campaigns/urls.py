from django.urls import path
from . import views

app_name = "campaigns"

urlpatterns = [
    path("rsvp/<uuid:token>/", views.rsvp_view, name="rsvp"),
    path("thanks/", views.thanks_view, name="thanks"),
]

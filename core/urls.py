from django.urls import path
from . import views

urlpatterns = [
    # Home page for RSVP landing
    path("", views.rsvp_home, name="home"),
]


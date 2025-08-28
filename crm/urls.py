
from django.urls import path, include
from rest_framework import routers
from .api import ContactViewSet, NoteViewSet
from . import views

app_name = "crm"
router = routers.DefaultRouter()
router.register(r"contacts", ContactViewSet, basename="crm-contacts")
router.register(r"notes", NoteViewSet, basename="crm-notes")

urlpatterns = [
    # HTML views (admin only)
    path("contacts/", views.contacts_list, name="contacts_list"),
    path("contacts/new/", views.contact_create, name="contact_create"),
    path("contacts/<int:pk>/edit/", views.contact_edit, name="contact_edit"),
    path("notes/", views.notes_list, name="notes_list"),
    path("notes/new/", views.note_create, name="note_create"),
    # API
    path("api/", include(router.urls)),
]

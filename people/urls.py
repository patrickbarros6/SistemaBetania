
from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "people"
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="people:members_list", permanent=False)),
    path("members/", views.members_list, name="members_list"),
    path("members/api/", views.members_api, name="members_api"),
    # HTMX/CRUD moderno
    path("members/form/", views.member_form, name="member_form"),
    path("members/save/", views.member_save, name="member_save"),
    path("members/<int:pk>/toggle/", views.member_toggle, name="member_toggle"),
    path("members/<int:pk>/delete/", views.member_delete, name="member_delete"),
    path("members/bulk-delete/", views.member_bulk_delete, name="member_bulk_delete"),
    path("members/import/", views.member_import_csv, name="member_import_csv"),
    path("members/new/", views.member_create, name="member_create"),
    path("members/<int:pk>/edit/", views.member_edit, name="member_edit"),
    path("members/<int:pk>/deactivate/", views.member_deactivate, name="member_deactivate"),
    path("unavailability/", views.unavailability_list, name="unavailability_list"),
    path("unavailability/new/", views.unavailability_create, name="unavailability_create"),
    path("unavailability/<int:pk>/edit/", views.unavailability_edit, name="unavailability_edit"),
    path("unavailability/<int:pk>/delete/", views.unavailability_delete, name="unavailability_delete"),
]

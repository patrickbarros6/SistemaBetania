
from django.urls import path
from . import views

app_name = "people"
urlpatterns = [
    path("members/", views.members_list, name="members_list"),
    path("members/new/", views.member_create, name="member_create"),
    path("members/<int:pk>/edit/", views.member_edit, name="member_edit"),
    path("members/<int:pk>/deactivate/", views.member_deactivate, name="member_deactivate"),
    path("unavailability/", views.unavailability_list, name="unavailability_list"),
    path("unavailability/new/", views.unavailability_create, name="unavailability_create"),
    path("unavailability/<int:pk>/edit/", views.unavailability_edit, name="unavailability_edit"),
    path("unavailability/<int:pk>/delete/", views.unavailability_delete, name="unavailability_delete"),
]

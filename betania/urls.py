from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core import views as core_views
from django.urls import include, path
from accounts import views as acc_views


    

router = routers.DefaultRouter()
router.register(r"members", core_views.MemberViewSet, basename="members")
router.register(r"member-prefs", core_views.MemberPrefViewSet, basename="memberprefs")
router.register(r"unavailability", core_views.UnavailabilityViewSet, basename="unavailability")
router.register(r"campaigns", core_views.CampaignViewSet, basename="campaigns")
router.register(r"invites", core_views.InviteViewSet, basename="invites")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/me/", core_views.me, name="me"),
    path("api/", include(router.urls)),
    path("", include("core.urls")), 
    path("rsvp/<str:token>/", core_views.rsvp_form, name="rsvp"),
    path("thanks/", core_views.thanks, name="thanks"),
    path("crm/", include("crm.urls")), 
    path("events/", include("events.urls")),
    path("people/", include("people.urls")),
    path("schedules/", include("schedules.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout/password
]

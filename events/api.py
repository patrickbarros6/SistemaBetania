
from rest_framework import viewsets, permissions
from .models import Event, Reservation
from .serializers import EventSerializer, ReservationSerializer

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.action in ["create","update","partial_update","destroy"]:
            return [IsAdmin()]
        return super().get_permissions()

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("event","contact").all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.action in ["create","update","partial_update","destroy"]:
            return [IsAdmin()]
        return super().get_permissions()

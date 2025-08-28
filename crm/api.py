
from rest_framework import viewsets, permissions
from .models import Contact, Note
from .serializers import ContactSerializer, NoteSerializer

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by("name")
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]  # leitura p/ autenticado
    def get_permissions(self):
        if self.action in ["create","update","partial_update","destroy"]:
            return [IsAdmin()]
        return super().get_permissions()

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.select_related("contact").all()
    serializer_class = NoteSerializer
    permission_classes = [IsAdmin]

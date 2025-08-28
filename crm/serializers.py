
from rest_framework import serializers
from .models import Contact, Note

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id","name","phone","email","tags","opt_in","active","created_at"]

class NoteSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.name", read_only=True)
    class Meta:
        model = Note
        fields = ["id","contact","contact_name","text","created_at"]

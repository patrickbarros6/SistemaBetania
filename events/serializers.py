
from rest_framework import serializers
from .models import Event, Reservation

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id","title","start_time","end_time","location","capacity","description","is_public","created_at"]

class ReservationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    class Meta:
        model = Reservation
        fields = ["id","event","event_title","contact","name","phone","email","created_at","checked_in_at"]

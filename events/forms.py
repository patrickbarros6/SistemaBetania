
from django import forms
from .models import Event, Reservation
from crm.models import Contact

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title","start_time","end_time","location","capacity","description","is_public"]
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control"}),
            "start_time": forms.TextInput(attrs={"class":"form-control","placeholder":"YYYY-MM-DD HH:MM"}),
            "end_time": forms.TextInput(attrs={"class":"form-control","placeholder":"YYYY-MM-DD HH:MM"}),
            "location": forms.TextInput(attrs={"class":"form-control"}),
            "capacity": forms.NumberInput(attrs={"class":"form-control"}),
            "description": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "is_public": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["contact","name","phone","email"]
        widgets = {
            "contact": forms.Select(attrs={"class":"form-select"}),
            "name": forms.TextInput(attrs={"class":"form-control"}),
            "phone": forms.TextInput(attrs={"class":"form-control"}),
            "email": forms.EmailInput(attrs={"class":"form-control"}),
        }

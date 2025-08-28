
from django import forms
from .models import Event, Reservation
from crm.models import Contact

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title","start_time","end_time","location","capacity","description","is_public"]
        widgets = {
            "title": forms.TextInput(attrs={"class":"input input-bordered w-full"}),
            "start_time": forms.TextInput(attrs={"class":"input input-bordered w-full","placeholder":"YYYY-MM-DD HH:MM"}),
            "end_time": forms.TextInput(attrs={"class":"input input-bordered w-full","placeholder":"YYYY-MM-DD HH:MM"}),
            "location": forms.TextInput(attrs={"class":"input input-bordered w-full"}),
            "capacity": forms.NumberInput(attrs={"class":"input input-bordered w-full"}),
            "description": forms.Textarea(attrs={"class":"textarea textarea-bordered w-full","rows":3}),
            "is_public": forms.CheckboxInput(attrs={"class":"checkbox"}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["contact","name","phone","email"]
        widgets = {
            "contact": forms.Select(attrs={"class":"select select-bordered w-full"}),
            "name": forms.TextInput(attrs={"class":"input input-bordered w-full"}),
            "phone": forms.TextInput(attrs={"class":"input input-bordered w-full"}),
            "email": forms.EmailInput(attrs={"class":"input input-bordered w-full"}),
        }

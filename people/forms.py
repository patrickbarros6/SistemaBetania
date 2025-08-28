
from django import forms
from core.models import Member, Unavailability

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["name", "phone", "kitchen_eligible", "active"]
        widgets = {
            "name": forms.TextInput(attrs={"class":"form-control"}),
            "phone": forms.TextInput(attrs={"class":"form-control", "placeholder":"+55... ou +54..."}),
            "kitchen_eligible": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "active": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }

class UnavailabilityForm(forms.ModelForm):
    class Meta:
        model = Unavailability
        fields = ["member", "date", "role", "note"]
        widgets = {
            "member": forms.Select(attrs={"class":"form-select"}),
            "date": forms.TextInput(attrs={"class":"form-control", "placeholder":"YYYY-MM-DD"}),
            "role": forms.Select(attrs={"class":"form-select"}),
            "note": forms.Textarea(attrs={"class":"form-control", "rows":3, "placeholder":"Motivo (opcional)"}),
        }

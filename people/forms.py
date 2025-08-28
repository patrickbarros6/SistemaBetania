
from django import forms
from core.models import Member, Unavailability

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["name", "phone", "kitchen_eligible", "active"]
        widgets = {
            "name": forms.TextInput(attrs={"class":"input input-bordered w-full"}),
            "phone": forms.TextInput(attrs={"class":"input input-bordered w-full","placeholder":"+55... ou +54..."}),
            "kitchen_eligible": forms.CheckboxInput(attrs={"class":"checkbox"}),
            "active": forms.CheckboxInput(attrs={"class":"checkbox"}),
        }

class UnavailabilityForm(forms.ModelForm):
    class Meta:
        model = Unavailability
        fields = ["member", "date", "role", "note"]
        widgets = {
            "member": forms.Select(attrs={"class":"select select-bordered w-full"}),
            "date": forms.TextInput(attrs={"class":"input input-bordered w-full", "placeholder":"YYYY-MM-DD"}),
            "role": forms.Select(attrs={"class":"select select-bordered w-full"}),
            "note": forms.Textarea(attrs={"class":"textarea textarea-bordered w-full", "rows":3, "placeholder":"Motivo (opcional)"}),
        }

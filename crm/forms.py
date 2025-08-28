
from django import forms
from .models import Contact, Note

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name","phone","email","tags","opt_in","active"]
        widgets = {
            "name": forms.TextInput(attrs={"class":"form-control"}),
            "phone": forms.TextInput(attrs={"class":"form-control","placeholder":"+55... / +54..."}),
            "email": forms.EmailInput(attrs={"class":"form-control"}),
            "tags": forms.TextInput(attrs={"class":"form-control","placeholder":"música, liderança, cozinha..."}),
            "opt_in": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "active": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["contact","text"]
        widgets = {
            "contact": forms.Select(attrs={"class":"form-select"}),
            "text": forms.Textarea(attrs={"class":"form-control","rows":3}),
        }

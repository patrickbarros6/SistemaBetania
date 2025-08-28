from django import forms

class RSVPForm(forms.Form):
    unavailable_dates = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    reason = forms.CharField(widget=forms.Textarea, required=False)

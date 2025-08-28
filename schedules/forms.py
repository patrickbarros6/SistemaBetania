from django import forms
import calendar, datetime


def month_sundays(year: int, month: int):
    cal = calendar.Calendar(firstweekday=6)
    return [d for w in cal.monthdatescalendar(year, month) for d in w if d.month == month and d.weekday() == 6]


class GenerateScheduleForm(forms.Form):
    year = forms.IntegerField(
        min_value=2000,
        max_value=2100,
        initial=datetime.date.today().year,
        label="Ano",
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    month = forms.IntegerField(
        min_value=1,
        max_value=12,
        initial=datetime.date.today().month,
        label="Mês",
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    min_days_between = forms.IntegerField(
        min_value=0,
        max_value=60,
        initial=21,
        label="Mínimo de dias entre serviços",
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    max_per_month = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=1,
        label="Máximo de funções por pessoa neste mês",
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    # checkboxes dinâmicos criados na view
    extra_dates = forms.CharField(
        required=False,
        label="Datas extras (YYYY-MM-DD, separadas por vírgula)",
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "2025-09-07, 2025-09-21"}),
    )


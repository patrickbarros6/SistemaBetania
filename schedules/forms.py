
from django import forms
import calendar, datetime

def month_sundays(year:int, month:int):
    cal = calendar.Calendar(firstweekday=6)
    return [d for w in cal.monthdatescalendar(year, month) for d in w if d.month==month and d.weekday()==6]

class GenerateScheduleForm(forms.Form):
    year = forms.IntegerField(min_value=2000, max_value=2100, initial=datetime.date.today().year, label="Ano")
    month = forms.IntegerField(min_value=1, max_value=12, initial=datetime.date.today().month, label="Mês")
    min_days_between = forms.IntegerField(min_value=0, max_value=60, initial=21, label="Mínimo de dias entre serviços")
    max_per_month = forms.IntegerField(min_value=1, max_value=5, initial=1, label="Máximo de funções por pessoa neste mês")
    # checkboxes de domingos (preenche dinamicamente na view)
    # campo para datas extras
    extra_dates = forms.CharField(required=False, label="Datas extras (YYYY-MM-DD, separadas por vírgula)")

import json
from .models import MemberPref
PT_MONTHS = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
ES_MONTHS = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}
def month_name(lang, month): return (PT_MONTHS if lang=='pt' else ES_MONTHS).get(month, str(month))
def format_dates_list(dates, lang): return ", ".join([d.strftime("%d/%m") for d in dates])
DEFAULT_TEMPLATES = {
 "pt":{"invite":"Olá {name}, tudo bem? Aqui é o automatizador de escalas da {church_name}.\nEstamos atualizando a base antes de gerar as escalas de {month_name}/{year}.\n\nDomingos do mês: {dates_list}\n\n⚠️ Em quais datas você NÃO poderá servir?\nResponda aqui: {rsvp_link}\n\nSe puder em todas, marque 'Posso em qualquer data'. Obrigado! 🙏",
       "reminder":"Olá {name}! Lembrete da nossa pesquisa para {month_name}/{year}. Você pode responder rapidinho aqui: {rsvp_link} 🙏"},
 "es":{"invite":"Hola {name}, ¿todo bien? Soy el automatizador de escalas de {church_name}.\nEstamos actualizando la base antes de generar las escalas de {month_name}/{year}.\n\nDomingos del mes: {dates_list}\n\n⚠️ ¿En cuáles fechas NO podrás servir?\nResponde aquí: {rsvp_link}\n\nSi puedes en todas, marca 'Puedo en cualquiera'. ¡Gracias! 🙏",
       "reminder":"¡Hola {name}! Recordatorio de nuestra encuesta para {month_name}/{year}. Responde aquí: {rsvp_link} 🙏"}
}
def parse_campaign_templates(raw):
    if not raw: return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict): return data
    except Exception:
        pass
    return {"pt":{"invite":raw},"es":{"invite":raw}}
def detect_lang_for_member(member):
    pref = MemberPref.objects.filter(member=member).first()
    if pref and pref.language in ("pt","es"): return pref.language
    phone = (member.phone or "").strip()
    if phone.startswith("+54"): return "es"
    if phone.startswith("+55"): return "pt"
    return "pt"
def render_message(kind, lang, context, campaign_raw_template):
    templates = {"pt": DEFAULT_TEMPLATES["pt"].copy(), "es": DEFAULT_TEMPLATES["es"].copy()}
    cam = parse_campaign_templates(campaign_raw_template)
    for l in ("pt","es"):
        if l in cam and isinstance(cam[l], dict):
            templates[l].update(cam[l])
        elif l in cam and isinstance(cam[l], str):
            templates[l]["invite"] = cam[l]
    tpl = templates.get(lang, templates["pt"]).get(kind)
    return tpl.format_map(context)

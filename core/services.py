from datetime import datetime, timedelta


# Estes stubs simulam dados. Substitua por queries reais.


def get_today_events(user):
    today = datetime.now().date()
    return [
    {"title": "Culto de Oração", "start": f"{today} 19:30", "location": "Templo"},
    {"title": "Ensaio Louvor", "start": f"{today} 18:00", "location": "Sala 2"},
    ]




def get_user_assignments(user, limit=5):
    return [
    {"date": "2025-09-01", "role": "Voz Principal", "team": "Louvor", "status": "Pendente"},
    {"date": "2025-09-08", "role": "Guitarra", "team": "Louvor", "status": "Confirmado"},
    ][:limit]




def get_pending_actions(user):
    return {
    "confirmations": 2, # ex.: precisa confirmar 2 escalas
    "swaps": 1, # ex.: 1 solicitação de troca
    "approvals": 0, # ex.: aprovações se for líder/admin
    }




def get_kpis_for(user):
    # Ex.: KPIs mudam por papel
    return [
    {"label": "Pessoas ativas no mês", "value": 128},
    {"label": "Presença média (7d)", "value": "72%"},
    {"label": "% confirmações de escala", "value": "84%"},
    ]




def get_announcements(user, limit=3):
    return [
    {"title": "Campanha de Jejum", "text": "Semana de oração e jejum – participe!"},
    {"title": "Mudança de horário", "text": "Culto de domingo agora às 10h."},
    ][:limit]
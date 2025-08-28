from django.contrib.auth.models import Group


def _is_admin(user):
    return bool(user and (user.is_superuser or user.is_staff or user.groups.filter(name__in=["admin"]).exists()))


def _build_base_nav(user):
    """Primary navigation matching existing routes in the project."""
    nav = [
        {"label": "Dashboard", "href": "/accounts/dashboard/", "starts": ["/accounts/dashboard", "/"]},
        {
            "label": "Pessoas",
            "href": "/people/",
            "starts": ["/people/"],
            "children": [
                {"label": "Membros", "href": "/people/members/"},
                {"label": "Indisponibilidades", "href": "/people/unavailability/"},
            ],
        },
        {
            "label": "Agenda",
            "href": "/events/manage/",
            "starts": ["/events/"],
            "children": [
                {"label": "Eventos", "href": "/events/manage/"},
                {"label": "Público", "href": "/events/public/"},
            ],
        },
        {
            "label": "Escalas",
            "href": "/schedules/",
            "starts": ["/schedules/"],
            "children": [
                {"label": "Minhas Escalas", "href": "/schedules/"},
                {"label": "Montar Escala", "href": "/schedules/generate/"},
            ],
        },
        {
            "label": "Comunicações",
            "href": "/crm/contacts/",
            "starts": ["/crm/", "/api/campaigns/"],
            "children": [
                {"label": "Contatos (CRM)", "href": "/crm/contacts/"},
                {"label": "Campanhas (API)", "href": "/api/campaigns/"},
            ],
        },
        {"label": "Relatórios", "href": "/schedules/", "starts": ["/schedules/"]},
    ]
    if _is_admin(user):
        nav.append({"label": "Configurações", "href": "/admin/", "starts": ["/admin/"], "children": []})
    return nav


def _mark_active(items, path):
    for it in items:
        it["active"] = any(path.startswith(pfx) for pfx in it.get("starts", [])) or path == it["href"]
        for ch in it.get("children", []):
            ch["active"] = path.startswith(ch["href"])
        it["open"] = it["active"] or any(ch.get("active") for ch in it.get("children", []))
    return items


def global_nav(request):
    nav = _build_base_nav(request.user)
    nav = _mark_active(nav, request.path)
    create_actions = [
        {"label": "Criar Evento", "href": "/events/manage/new/"},
        {"label": "Criar Escala", "href": "/schedules/generate/"},
        {"label": "Nova Campanha (API)", "href": "/api/campaigns/"},
        {"label": "Novo Membro", "href": "/people/members/new/"},
    ]
    return {"NAV": nav, "CREATE_ACTIONS": create_actions}


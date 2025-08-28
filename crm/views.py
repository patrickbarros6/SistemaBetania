
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Contact, Note
from .forms import ContactForm, NoteForm

def is_admin(u): return bool(u and u.is_authenticated and u.is_staff)

@login_required
@user_passes_test(is_admin)
def contacts_list(request):
    q = request.GET.get("q","").strip()
    qs = Contact.objects.all()
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(tags__icontains=q) | qs.filter(phone__icontains=q) | qs.filter(email__icontains=q)
    return render(request, "crm/contacts_list.html", {"contacts": qs, "q": q})

@login_required
@user_passes_test(is_admin)
def contact_create(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Contato criado.")
            return redirect("crm:contacts_list")
    else:
        form = ContactForm()
    return render(request, "crm/contact_form.html", {"form": form, "title": "Novo contato"})

@login_required
@user_passes_test(is_admin)
def contact_edit(request, pk:int):
    c = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            messages.success(request, "Contato salvo.")
            return redirect("crm:contacts_list")
    else:
        form = ContactForm(instance=c)
    return render(request, "crm/contact_form.html", {"form": form, "title": f"Editar — {c.name}"})

@login_required
@user_passes_test(is_admin)
def notes_list(request):
    qs = Note.objects.select_related("contact").all()
    return render(request, "crm/notes_list.html", {"notes": qs})

@login_required
@user_passes_test(is_admin)
def note_create(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nota adicionada.")
            return redirect("crm:notes_list")
    else:
        form = NoteForm()
    return render(request, "crm/note_form.html", {"form": form, "title": "Nova nota"})

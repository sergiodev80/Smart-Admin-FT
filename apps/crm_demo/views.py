import json

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from .models import CallLog, Contact, EmailLog, Purchase, SocialProfile
from .services import ContactService


def _admin_context(request):
    return admin.site.each_context(request)


@staff_member_required
def contact_list(request):
    from .dashboard import get_crm_cards

    status_filter = request.GET.get("status", "")
    qs = Contact.objects.all()
    if status_filter:
        qs = qs.filter(status=status_filter)

    tabs = [
        {"label": str(_("Todos")), "url": "?", "active": not status_filter, "count_url": ""},
        {"label": str(_("Leads")), "url": "?status=lead", "active": status_filter == "lead", "count_url": f"{request.path}counts/?status=lead", "count_type": "info"},
        {"label": str(_("Prospectos")), "url": "?status=prospect", "active": status_filter == "prospect", "count_url": f"{request.path}counts/?status=prospect", "count_type": "warning"},
        {"label": str(_("Clientes")), "url": "?status=client", "active": status_filter == "client", "count_url": f"{request.path}counts/?status=client", "count_type": "success"},
        {"label": str(_("Inactivos")), "url": "?status=inactive", "active": status_filter == "inactive", "count_url": f"{request.path}counts/?status=inactive"},
    ]

    context = _admin_context(request)
    context.update({
        "contacts": qs,
        "tabs": tabs,
        "status_filter": status_filter,
        "stat_cards": get_crm_cards(request),
    })
    return render(request, "crm_demo/contact_list.html", context)


@staff_member_required
def contact_list_items(request):
    status_filter = request.GET.get("status", "")
    qs = Contact.objects.all()
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, "crm_demo/contact_list_items.html", {"contacts": qs, "status_filter": status_filter})


@staff_member_required
def contact_counts(request):
    status = request.GET.get("status", "")
    count = Contact.objects.filter(status=status).count() if status else Contact.objects.count()
    return HttpResponse(str(count))


@staff_member_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    items = [
        {"label": str(_("Nombre")),   "value": contact.name},
        {"label": str(_("Email")),    "value": contact.email},
        {"label": str(_("Empresa")),  "value": contact.company or "—"},
        {"label": str(_("Estado")),   "value": contact.get_status_display()},
        {"label": str(_("Teléfono")), "value": contact.phone or "—"},
        {"label": str(_("Creado")),   "value": contact.created_at.strftime("%d/%m/%Y %H:%M")},
    ]
    return render(request, "crm_demo/contact_detail.html", {
        "contact": contact,
        "items": items,
        "purchases": contact.purchases.all(),
        "email_logs": contact.email_logs.all(),
        "call_logs": contact.call_logs.all(),
        "social_profiles": contact.social_profiles.all(),
    })


@staff_member_required
@require_http_methods(["GET", "PATCH"])
def contact_inline_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    allowed_fields = {"phone", "company"}

    if request.method == "PATCH":
        data = json.loads(request.body)
        field = data.get("field")
        value = data.get("value", "")
        if field not in allowed_fields:
            return HttpResponse(status=400)
        setattr(contact, field, value)
        contact.save(update_fields=[field])
        response = render(request, "unfold/components/inline_edit.html", {
            "value": getattr(contact, field),
            "field": field,
            "url": request.path,
            "field_type": "text",
        })
        response["HX-Trigger"] = json.dumps({
            "showToast": {"type": "success", "title": str(_("Guardado")), "body": ""}
        })
        return response

    field = request.GET.get("field", "phone")
    return render(request, "unfold/components/inline_edit.html", {
        "value": getattr(contact, field, ""),
        "field": field,
        "url": request.path,
        "field_type": "text",
    })


@staff_member_required
def contact_create(request):
    from django import forms as django_forms

    class ContactForm(django_forms.Form):
        name    = django_forms.CharField(max_length=200, label=str(_("Nombre")))
        email   = django_forms.EmailField(label=str(_("Email")))
        phone   = django_forms.CharField(max_length=50, required=False, label=str(_("Teléfono")))
        company = django_forms.CharField(max_length=200, required=False, label=str(_("Empresa")))
        status  = django_forms.ChoiceField(choices=Contact.STATUS_CHOICES, label=str(_("Estado")))

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                ContactService.create(form.cleaned_data, created_by=request.user)
                response = HttpResponse(status=204)
                response["HX-Trigger"] = json.dumps({
                    "showToast": {"type": "success", "title": str(_("Contacto creado")), "body": ""},
                    "refreshContacts": {},
                })
                return response
            except ValueError as e:
                form.add_error(None, str(e))
        return render(request, "crm_demo/contact_create_modal.html", {"form": form})

    form = ContactForm()
    return render(request, "crm_demo/contact_create_modal.html", {"form": form})


@staff_member_required
@require_http_methods(["POST"])
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    response = HttpResponse(status=204)
    response["HX-Trigger"] = json.dumps({
        "showToast": {"type": "success", "title": str(_("Contacto eliminado")), "body": ""},
    })
    response["HX-Redirect"] = "/admin/crm-demo/contacts/"
    return response

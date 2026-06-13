from django import template
from django.urls import reverse

register = template.Library()


@register.filter
def url_inline_edit(contact):
    return reverse("crm_contact_inline_edit", kwargs={"pk": contact.pk})


@register.filter
def url_contact_delete(contact):
    return reverse("crm_contact_delete", kwargs={"pk": contact.pk})


@register.filter
def url_contact_detail(contact):
    return reverse("crm_contact_detail", kwargs={"pk": contact.pk})

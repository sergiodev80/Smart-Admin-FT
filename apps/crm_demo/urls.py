from django.urls import path

from . import views

urlpatterns = [
    path("contacts/",                      views.contact_list,        name="crm_contact_list"),
    path("contacts/items/",                views.contact_list_items,  name="crm_contact_items"),
    path("contacts/create/",               views.contact_create,      name="crm_contact_create"),
    path("contacts/counts/",               views.contact_counts,      name="crm_contact_counts"),
    path("contacts/<int:pk>/detail/",      views.contact_detail,      name="crm_contact_detail"),
    path("contacts/<int:pk>/inline-edit/", views.contact_inline_edit, name="crm_contact_inline_edit"),
    path("contacts/<int:pk>/delete/",      views.contact_delete,      name="crm_contact_delete"),
]

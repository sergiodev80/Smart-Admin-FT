from django.urls import path
from . import views

urlpatterns = [
    path("unread-count/", views.unread_count_view, name="notifications_unread_count"),
    path("unread-list/", views.unread_list_view, name="notifications_unread_list"),
    path("mark-read/", views.mark_read_view, name="notifications_mark_read"),
]

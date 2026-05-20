from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.core.forms import PlatformAuthenticationForm
from apps.core.views import solicitar_acceso

admin.site.login_form = PlatformAuthenticationForm

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/password_reset/", auth_views.PasswordResetView.as_view(), name="admin_password_reset"),
    path("admin/password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("admin/", admin.site.urls),
    path("solicitar-acceso/", solicitar_acceso, name="request_access"),
    path("traducciones/", include("apps.translations.urls")),
]

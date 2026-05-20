from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from unfold.forms import AuthenticationForm as UnfoldAuthenticationForm


class SolicitudAccesoForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "tu@solid.com.py"}),
    )


class PlatformAuthenticationForm(UnfoldAuthenticationForm):
    """Login form que permite acceso a cualquier usuario activo, no solo staff."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Username / Email")

    def confirm_login_allowed(self, user):
        AuthenticationForm.confirm_login_allowed(self, user)

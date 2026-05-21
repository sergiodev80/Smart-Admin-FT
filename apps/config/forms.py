from django import forms
from django.utils.translation import gettext_lazy as _

from .models import SiteConfig


class SiteConfigForm(forms.ModelForm):
    class Meta:
        model = SiteConfig
        fields = ("key", "value_type", "value", "description", "is_public")
        widgets = {
            "description": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        value_type = None

        if instance:
            value_type = instance.value_type
        elif self.data:
            value_type = self.data.get("value_type")

        if value_type == SiteConfig.ValueType.BOOL:
            self.fields["value"] = forms.ChoiceField(
                choices=[("true", _("Verdadero")), ("false", _("Falso"))],
                label=_("valor"),
                help_text=_("Siempre almacenado como texto."),
            )
        elif value_type == SiteConfig.ValueType.INT:
            self.fields["value"] = forms.IntegerField(
                label=_("valor"),
                help_text=_("Siempre almacenado como texto."),
            )

            def int_to_str(value):
                return value

            self.fields["value"].prepare_value = int_to_str
        else:
            self.fields["value"].widget = forms.Textarea(attrs={"rows": 3})

    def clean_value(self):
        value = self.cleaned_data.get("value")
        return str(value)

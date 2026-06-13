from django.db import models
from django.utils.translation import gettext_lazy as _


class Contact(models.Model):
    STATUS_LEAD = "lead"
    STATUS_PROSPECT = "prospect"
    STATUS_CLIENT = "client"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_LEAD, _("Lead")),
        (STATUS_PROSPECT, _("Prospecto")),
        (STATUS_CLIENT, _("Cliente")),
        (STATUS_INACTIVE, _("Inactivo")),
    ]

    name       = models.CharField(_("nombre"), max_length=200)
    email      = models.EmailField(_("email"), unique=True)
    phone      = models.CharField(_("teléfono"), max_length=50, blank=True)
    company    = models.CharField(_("empresa"), max_length=200, blank=True)
    status     = models.CharField(_("estado"), max_length=20, choices=STATUS_CHOICES, default=STATUS_LEAD)
    created_at = models.DateTimeField(_("creado el"), auto_now_add=True)

    class Meta:
        verbose_name = _("Contacto")
        verbose_name_plural = _("Contactos")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Purchase(models.Model):
    contact     = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="purchases", verbose_name=_("contacto"))
    amount      = models.DecimalField(_("monto"), max_digits=10, decimal_places=2)
    description = models.CharField(_("descripción"), max_length=300)
    date        = models.DateField(_("fecha"))

    class Meta:
        verbose_name = _("Compra")
        verbose_name_plural = _("Compras")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.contact.name} — ${self.amount}"


class EmailLog(models.Model):
    DIRECTION_IN = "in"
    DIRECTION_OUT = "out"
    DIRECTION_CHOICES = [
        (DIRECTION_IN, _("Entrante")),
        (DIRECTION_OUT, _("Saliente")),
    ]

    contact   = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="email_logs", verbose_name=_("contacto"))
    subject   = models.CharField(_("asunto"), max_length=200)
    body      = models.TextField(_("cuerpo"), blank=True)
    date      = models.DateTimeField(_("fecha"))
    direction = models.CharField(_("dirección"), max_length=3, choices=DIRECTION_CHOICES)

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.subject} ({self.direction})"


class CallLog(models.Model):
    DIRECTION_IN = "in"
    DIRECTION_OUT = "out"
    DIRECTION_CHOICES = [
        (DIRECTION_IN, _("Entrante")),
        (DIRECTION_OUT, _("Saliente")),
    ]

    contact          = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="call_logs", verbose_name=_("contacto"))
    duration_minutes = models.PositiveIntegerField(_("duración (minutos)"))
    notes            = models.TextField(_("notas"), blank=True)
    date             = models.DateTimeField(_("fecha"))
    direction        = models.CharField(_("dirección"), max_length=3, choices=DIRECTION_CHOICES)

    class Meta:
        verbose_name = _("Llamada")
        verbose_name_plural = _("Llamadas")
        ordering = ["-date"]

    def __str__(self):
        return f"Llamada {self.direction} — {self.duration_minutes}min"


class SocialProfile(models.Model):
    NETWORK_LINKEDIN  = "linkedin"
    NETWORK_TWITTER   = "twitter"
    NETWORK_INSTAGRAM = "instagram"
    NETWORK_FACEBOOK  = "facebook"
    NETWORK_CHOICES = [
        (NETWORK_LINKEDIN,  "LinkedIn"),
        (NETWORK_TWITTER,   "Twitter"),
        (NETWORK_INSTAGRAM, "Instagram"),
        (NETWORK_FACEBOOK,  "Facebook"),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="social_profiles", verbose_name=_("contacto"))
    network = models.CharField(_("red social"), max_length=20, choices=NETWORK_CHOICES)
    url     = models.URLField(_("URL"))

    class Meta:
        verbose_name = _("Perfil social")
        verbose_name_plural = _("Perfiles sociales")
        unique_together = [("contact", "network")]

    def __str__(self):
        return f"{self.contact.name} — {self.network}"

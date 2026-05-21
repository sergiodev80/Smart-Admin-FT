from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.erp_sync.services import ERPUserService

from .forms import SolicitudAccesoForm
from .models import User


def _send_activation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    protocol = "https" if request.is_secure() else "http"
    domain = request.get_host()
    context = {"uid": uid, "token": token, "protocol": protocol, "domain": domain, "user": user}
    body = render_to_string("registration/activation_email.html", context)
    subject_raw = render_to_string("registration/activation_subject.txt", context)
    subject = "".join(subject_raw.splitlines()).strip()
    send_mail(subject, body, None, [user.email], fail_silently=False)


def solicitar_acceso(request):
    if request.method == "POST":
        form = SolicitudAccesoForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            # Verificar si ya existe en Django
            if User.objects.filter(email=email).exists():
                messages.error(request, "Ya existe una cuenta con este email.")
                return render(request, "core/request_access.html", {"form": form})

            # Buscar en ERP
            erp_user = ERPUserService.find_by_email(email)
            if not erp_user:
                messages.error(
                    request,
                    "El email no está registrado como colaborador activo en el sistema.",
                )
                return render(request, "core/request_access.html", {"form": form})

            # Crear usuario con is_staff=True (requerido por Unfold AdminAuthenticationForm)
            user = User.objects.create(
                username=email,
                email=email,
                first_name=erp_user.get("name") or "",
                erp_employee_id=str(erp_user.get("login")),
                is_active=True,
                is_staff=True,
            )
            user.set_unusable_password()
            user.save()

            # Enviar email de activación con token directo
            # (PasswordResetForm omite usuarios sin contraseña usable)
            try:
                _send_activation_email(request, user)
            except Exception:
                pass

            messages.success(
                request,
                "Te enviamos un email con instrucciones para activar tu cuenta.",
            )
            return redirect("request_access")
    else:
        form = SolicitudAccesoForm()

    return render(request, "core/request_access.html", {"form": form})

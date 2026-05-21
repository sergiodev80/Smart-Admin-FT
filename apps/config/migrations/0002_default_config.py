from django.db import migrations


DEFAULT_CONFIGS = [
    # Identidad del sitio
    {
        "key": "site_name",
        "value": "Mi Proyecto",
        "value_type": "str",
        "description": "Nombre del sitio o proyecto.",
        "is_public": True,
    },
    {
        "key": "site_description",
        "value": "Descripción breve del proyecto.",
        "value_type": "str",
        "description": "Descripción corta del sitio.",
        "is_public": True,
    },
    {
        "key": "contact_email",
        "value": "contacto@example.com",
        "value_type": "str",
        "description": "Email de contacto principal.",
        "is_public": False,
    },
    # Comportamiento del sistema
    {
        "key": "max_upload_size_mb",
        "value": "10",
        "value_type": "int",
        "description": "Tamaño máximo de archivo subido en MB.",
        "is_public": False,
    },
    {
        "key": "session_timeout_minutes",
        "value": "60",
        "value_type": "int",
        "description": "Minutos de inactividad antes de cerrar sesión.",
        "is_public": False,
    },
    {
        "key": "items_per_page",
        "value": "25",
        "value_type": "int",
        "description": "Cantidad de ítems por página en listados.",
        "is_public": False,
    },
    # Feature flags
    {
        "key": "enable_notifications",
        "value": "true",
        "value_type": "bool",
        "description": "Habilitar el sistema de notificaciones.",
        "is_public": False,
    },
    {
        "key": "enable_audit",
        "value": "true",
        "value_type": "bool",
        "description": "Habilitar el registro de auditoría.",
        "is_public": False,
    },
    {
        "key": "enable_webhooks",
        "value": "false",
        "value_type": "bool",
        "description": "Habilitar el envío de notificaciones por webhook.",
        "is_public": False,
    },
    # Email y comunicaciones
    {
        "key": "email_from_name",
        "value": "Mi Proyecto",
        "value_type": "str",
        "description": "Nombre del remitente en los emails salientes.",
        "is_public": False,
    },
    {
        "key": "support_email",
        "value": "soporte@example.com",
        "value_type": "str",
        "description": "Email de soporte visible para los usuarios.",
        "is_public": True,
    },
    {
        "key": "email_footer_text",
        "value": "Este email fue enviado automáticamente. Por favor no responder.",
        "value_type": "str",
        "description": "Texto del pie de página en emails salientes.",
        "is_public": False,
    },
]


def create_default_configs(apps, schema_editor):
    SiteConfig = apps.get_model("config", "SiteConfig")
    for cfg in DEFAULT_CONFIGS:
        SiteConfig.objects.get_or_create(key=cfg["key"], defaults=cfg)


def delete_default_configs(apps, schema_editor):
    SiteConfig = apps.get_model("config", "SiteConfig")
    keys = [cfg["key"] for cfg in DEFAULT_CONFIGS]
    SiteConfig.objects.filter(key__in=keys).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_configs, reverse_code=delete_default_configs),
    ]

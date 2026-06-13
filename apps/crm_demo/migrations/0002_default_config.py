from django.db import migrations

CRM_CONFIGS = [
    {
        "key": "crm_demo_contact_max",
        "value": "500",
        "value_type": "int",
        "description": "Número máximo de contactos permitidos en la demo.",
        "is_public": False,
    },
]


def create_configs(apps, schema_editor):
    SiteConfig = apps.get_model("config", "SiteConfig")
    for cfg in CRM_CONFIGS:
        SiteConfig.objects.get_or_create(key=cfg["key"], defaults=cfg)


def delete_configs(apps, schema_editor):
    SiteConfig = apps.get_model("config", "SiteConfig")
    SiteConfig.objects.filter(key__in=[c["key"] for c in CRM_CONFIGS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("crm_demo", "0001_initial"),
        ("config", "0002_default_config"),
    ]

    operations = [
        migrations.RunPython(create_configs, reverse_code=delete_configs),
    ]

from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Activate all v2 apps for testing
LOCAL_APPS = [
    "apps.core",
    "apps.notifications",
    "apps.audit",
    "apps.config",
    "apps.permissions",
    "apps.crm_demo",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS  # noqa: F405

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="config.SiteConfig")
def invalidate_config_cache(sender, instance, **kwargs):
    from apps.config.services import ConfigService
    ConfigService.invalidate(instance.key)

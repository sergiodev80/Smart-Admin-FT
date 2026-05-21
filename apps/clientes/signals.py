from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.clientes.models import Cliente
from apps.clientes.services import ClienteService


@receiver(post_save, sender=Cliente)
def cliente_post_save(sender, instance, created, **kwargs):
    if created:
        ClienteService.notify_new_client(instance)

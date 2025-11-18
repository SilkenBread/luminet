from django.dispatch import Signal
from django.dispatch import receiver
from django.db.models.signals import post_save

from ..models import PqrActive


pqr_created = Signal()


@receiver(post_save, sender = PqrActive)
def notify_pqr_creation(sender, instance, created, **kwargs):
    # Emitir la señal personalizada cuando se crea una PQR
    pqr_created.send(sender=sender, instance=instance)

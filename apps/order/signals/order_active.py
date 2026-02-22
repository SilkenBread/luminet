from . import signals, receiver
from ..models import OrderActive, OrderActiveRoute


@receiver(signals.post_save, sender=OrderActive)
def post_save_order_active(sender, instance, created, **kwargs):
    if created:
        instance.date_limit = instance.date_creation + instance.fk_timingrepair.timing_reparation
        instance.save()

        routeInstance = OrderActiveRoute(
            fk_ot=instance, state=1, user_creation=instance.user_creation)
        routeInstance.save()

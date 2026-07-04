from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import CartOrder, OrderStatusHistory


@receiver(pre_save, sender=CartOrder)
def cache_old_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return

    try:
        old = CartOrder.objects.get(pk=instance.pk)
        instance._old_status = old.product_status
    except CartOrder.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=CartOrder)
def create_status_history(sender, instance, created, **kwargs):
    # নতুন Order হলে প্রথম status save করবে
    if created:
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.product_status,
        )
        return

    # Status change হলে নতুন history add করবে
    if getattr(instance, "_old_status", None) != instance.product_status:
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.product_status,
        )
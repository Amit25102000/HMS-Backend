"""
Prescription signals for stock management
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import PrescriptionMedicine


@receiver(post_save, sender=PrescriptionMedicine)
def deduct_stock_on_prescription(sender, instance, created, **kwargs):
    """Deduct medicine stock when prescription medicine is added"""
    if created and instance.prescription.status == 'COMPLETED':
        medicine = instance.medicine
        medicine.stock_quantity -= instance.quantity
        medicine.save()


@receiver(pre_delete, sender=PrescriptionMedicine)
def restore_stock_on_deletion(sender, instance, **kwargs):
    """Restore medicine stock when prescription medicine is deleted"""
    if instance.prescription.status == 'COMPLETED':
        medicine = instance.medicine
        medicine.stock_quantity += instance.quantity
        medicine.save()

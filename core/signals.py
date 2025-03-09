from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Application, CashFlow, Payment, Transactions


@receiver(post_save, sender=Application)
def handle_application_approval(sender, instance, created, **kwargs):
    if not (instance.status == "approved" and not created):
        return 
        
    total_amount = instance.amount * (1 + instance.interest_rate / 100)
    monthly_payment = total_amount / instance.duration_months

    tarx = Transactions.objects.create(
        user=instance.user,
        application=instance,
        start_date=timezone.now().date(),
        end_date=timezone.now().date()
        + timedelta(days=30 * instance.duration_months),
        monthly_payment=monthly_payment,
        total_amount=total_amount,
        is_active=True,
    )

    CashFlow.objects.create(
        transaction_type=(
            "deposit_received"
            if instance.application_type == "deposit"
            else "loan_issued"
        ),
        amount=instance.amount,
        date=timezone.now().date(),
        transaction=tarx,
    )

    for month in range(1, instance.duration_months + 1):
        Payment.objects.create(
            payment_type=instance.application_type,
            amount=monthly_payment,
            due_date=tarx.start_date + timedelta(days=30 * month),
            status="scheduled",
            transaction=tarx,
        )


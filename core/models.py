from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from .utils import PERCENTAGE_VALIDATOR

# Create your models here.


class User(AbstractUser):
    pass


class Application(models.Model):
    APPLICATION_TYPE_CHOICES = [
        ("deposit", "Deposit"),
        ("loan", "Loan"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved by Bank"),
        ("rejected", "Rejected by Bank"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(groups__name="Borrower")
        | models.Q(groups__name="Provider"),
    )
    application_type = models.CharField(
        max_length=20, choices=APPLICATION_TYPE_CHOICES
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    duration_months = models.IntegerField()
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=PERCENTAGE_VALIDATOR,
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        limit_choices_to={"groups__name": "Bank Personnel"},
        on_delete=models.SET_NULL,
        related_name="reviewed_applications",
    )

    def __str__(self):
        return f"{self.application_type} of {self.amount} by {self.user.username}"

    def clean(self):
        if self.application_type == "deposit":
            if not self.user.groups.filter(name="Provider").exists():
                raise ValidationError(
                    "Only providers can submit deposits", code="invalid"
                )
        elif self.application_type == "loan":
            if not self.user.groups.filter(name="Borrower").exists():
                raise ValidationError(
                    "Only borrowers can submit loans", code="invalid"
                )
            if self.status == 'approved' and self.amount > CashFlow.get_cash():
                raise ValidationError(
                    "Loan amount exceeds available funds",
                    code="insufficient",
                )


class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.OneToOneField(
        Application, on_delete=models.CASCADE
    )
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_payment = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Trx of {self.application}"


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ("deposit", "Deposit Payment"),
        ("loan", "Loan Repayment"),
    ]
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE_CHOICES
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    paid_date = models.DateField(null=True, blank=True)
    transaction = models.ForeignKey(
        Transactions, null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Payment of date {self.due_date}"


class CashFlow(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("deposit_received", "Deposit Received"),
        ("loan_issued", "Loan Issued"),
        ("deposit_payment", "Deposit Payment"),
        ("loan_payment", "Loan Payment"),
    ]

    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPE_CHOICES
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    transaction = models.ForeignKey(
        Transactions, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"Cash Flow of {self.transaction}"

    @classmethod
    def get_cash(self) -> int:
        all_transactions = CashFlow.objects.all()

        total_deposits = (
            all_transactions.filter(
                transaction_type="deposit_received"
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        total_loan_payments = (
            all_transactions.filter(
                transaction_type="loan_payment"
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        total_loans = (
            all_transactions.filter(
                transaction_type="loan_issued"
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        total_loan_payments = (
            all_transactions.filter(
                transaction_type="deposit_payment"
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        return (total_deposits + total_loan_payments) - (
            total_loans + total_loan_payments
        )

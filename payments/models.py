from django.conf import settings
from django.db import models
from django.db.models import Sum


class Transaction(models.Model):
    class Type(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        INVESTMENT = "investment", "Investment"
        COMMISSION = "commission", "Commission"
        PAYOUT = "payout", "Investment Payout"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=20, choices=Type.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    phone = models.CharField(max_length=20, blank=True)
    note = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def balance_for(cls, user):
        approved = cls.objects.filter(user=user, status=cls.Status.APPROVED)
        deposits = approved.filter(transaction_type=cls.Type.DEPOSIT).aggregate(total=Sum("amount"))["total"] or 0
        commissions = approved.filter(transaction_type=cls.Type.COMMISSION).aggregate(total=Sum("amount"))["total"] or 0
        payouts = approved.filter(transaction_type=cls.Type.PAYOUT).aggregate(total=Sum("amount"))["total"] or 0
        withdrawals = approved.filter(transaction_type=cls.Type.WITHDRAWAL).aggregate(total=Sum("amount"))["total"] or 0
        investments = approved.filter(transaction_type=cls.Type.INVESTMENT).aggregate(total=Sum("amount"))["total"] or 0
        return {
            "total_deposits": deposits,
            "referral_bonus": commissions,
            "total_withdrawals": withdrawals,
            "available_balance": deposits + commissions + payouts - withdrawals - investments,
        }

    def __str__(self):
        return f"{self.get_transaction_type_display()} KSh {self.amount}"

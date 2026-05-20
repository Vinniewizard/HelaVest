from django.utils import timezone

from payments.models import Transaction

from .models import Investment


def complete_matured_investments(user):
    matured = Investment.objects.filter(user=user, status=Investment.Status.ACTIVE, matures_at__lte=timezone.now())
    completed = 0
    for investment in matured:
        investment.status = Investment.Status.COMPLETED
        investment.save(update_fields=["status"])
        Transaction.objects.get_or_create(
            user=user,
            transaction_type=Transaction.Type.PAYOUT,
            note=f"Payout for {investment.plan.name} #{investment.id}",
            defaults={
                "amount": investment.return_amount,
                "status": Transaction.Status.APPROVED,
            },
        )
        completed += 1
    return completed

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import redirect, render

from payments.models import Transaction
from referrals.models import Referral

from .forms import InvestmentForm
from .models import Investment, Plan
from .services import complete_matured_investments


@login_required
def trades(request):
    complete_matured_investments(request.user)
    status = request.GET.get("status", "all")
    trades_qs = Investment.objects.filter(user=request.user).select_related("plan")
    if status in {Investment.Status.ACTIVE, Investment.Status.COMPLETED, Investment.Status.CANCELLED}:
        trades_qs = trades_qs.filter(status=status)

    all_trades = Investment.objects.filter(user=request.user)
    stats = {
        "total_trades": all_trades.count(),
        "active_trades": all_trades.filter(status=Investment.Status.ACTIVE).count(),
        "completed_trades": all_trades.filter(status=Investment.Status.COMPLETED).count(),
        "total_capital": all_trades.aggregate(total=Sum("amount"))["total"] or 0,
        "expected_returns": all_trades.aggregate(total=Sum("return_amount"))["total"] or 0,
    }
    return render(
        request,
        "investments/trades.html",
        {
            "trades": trades_qs,
            "active_trades": all_trades.filter(status=Investment.Status.ACTIVE).select_related("plan"),
            "selected_status": status,
            "stats": stats,
        },
    )


@login_required
@transaction.atomic
def invest(request):
    complete_matured_investments(request.user)
    form = InvestmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        plan = form.cleaned_data["plan"]
        balance = Transaction.balance_for(request.user)["available_balance"]
        if balance < plan.amount:
            messages.error(request, "Your available balance is not enough for this plan. Please deposit first.")
            return redirect("dashboard")

        Investment.objects.create(user=request.user, plan=plan, amount=plan.amount, return_amount=plan.return_amount, profit=plan.profit)
        Transaction.objects.create(
            user=request.user,
            amount=plan.amount,
            transaction_type=Transaction.Type.INVESTMENT,
            status=Transaction.Status.APPROVED,
            note=f"Started {plan.name}",
        )

        if request.user.referred_by:
            bonus = max(50, round(plan.amount * 0.08))
            Referral.objects.create(referrer=request.user.referred_by, referred_user=request.user, bonus=bonus)
            Transaction.objects.create(
                user=request.user.referred_by,
                amount=bonus,
                transaction_type=Transaction.Type.COMMISSION,
                status=Transaction.Status.APPROVED,
                note=f"Commission from {request.user.username}",
            )

        messages.success(request, f"{plan.name} started. Expected payout: KSh {plan.return_amount:,}.")
        return redirect("dashboard")

    plans = Plan.objects.filter(active=True)
    balance_data = Transaction.balance_for(request.user)
    active_trades = Investment.objects.filter(user=request.user, status=Investment.Status.ACTIVE).select_related("plan")
    completed_trades = Investment.objects.filter(user=request.user, status=Investment.Status.COMPLETED)
    stats = {
        "available_balance": balance_data["available_balance"],
        "active_count": active_trades.count(),
        "active_capital": active_trades.aggregate(total=Sum("amount"))["total"] or 0,
        "expected_active_returns": active_trades.aggregate(total=Sum("return_amount"))["total"] or 0,
        "completed_profit": completed_trades.aggregate(total=Sum("profit"))["total"] or 0,
        "plan_count": plans.count(),
        "starter_plan": plans.order_by("amount").first(),
        "popular_plan": plans.annotate(trade_count=Count("investment")).order_by("-trade_count", "amount").first(),
    }
    return render(
        request,
        "investments/invest.html",
        {
            "form": form,
            "plans": plans,
            "active_trades": active_trades[:4],
            "stats": stats,
        },
    )

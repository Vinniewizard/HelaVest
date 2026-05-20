from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from investments.models import Investment, Plan
from investments.services import complete_matured_investments
from payments.models import Transaction
from referrals.models import Referral

from .forms import RegisterForm


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created. Welcome to your investment dashboard.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


@login_required
def dashboard(request):
    user = request.user
    completed_count = complete_matured_investments(user)
    if completed_count:
        messages.success(request, f"{completed_count} matured trade payout credited to your balance.")
    plans = Plan.objects.filter(active=True).order_by("amount")
    active_trades = Investment.objects.filter(user=user, status=Investment.Status.ACTIVE).select_related("plan")
    trade_history = Investment.objects.filter(user=user).exclude(status=Investment.Status.ACTIVE).select_related("plan")[:10]
    transactions = Transaction.objects.filter(user=user)[:8]
    referrals = Referral.objects.filter(referrer=user).select_related("referred_user")[:8]
    completed_profit = (
        Investment.objects.filter(user=user, status=Investment.Status.COMPLETED).aggregate(total=Sum("profit"))["total"] or 0
    )
    totals = Transaction.balance_for(user)
    context = {
        "plans": plans,
        "active_trades": active_trades,
        "trade_history": trade_history,
        "transactions": transactions,
        "referrals": referrals,
        "available_balance": totals["available_balance"],
        "total_deposits": totals["total_deposits"],
        "total_withdrawals": totals["total_withdrawals"],
        "referral_bonus": totals["referral_bonus"],
        "completed_profit": completed_profit,
        "active_capital": active_trades.aggregate(total=Sum("amount"))["total"] or 0,
    }
    return render(request, "dashboard/index.html", context)

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import redirect, render

from investments.models import Investment
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
    active_trades = Investment.objects.filter(user=user, status=Investment.Status.ACTIVE).select_related("plan")
    trade_history = Investment.objects.filter(user=user).exclude(status=Investment.Status.ACTIVE).select_related("plan")[:10]
    transactions = Transaction.objects.filter(user=user)[:8]
    referrals = Referral.objects.filter(referrer=user).select_related("referred_user")[:8]
    completed_profit = (
        Investment.objects.filter(user=user, status=Investment.Status.COMPLETED).aggregate(total=Sum("profit"))["total"] or 0
    )
    totals = Transaction.balance_for(user)
    context = {
        "active_trades": active_trades,
        "trade_history": trade_history,
        "transactions": transactions,
        "referrals": referrals,
        "market_updates": [
            {
                "label": "Funding Network",
                "title": "Preferred lending partners across the USA, Australia, UK, UAE, and Kenya",
                "summary": "The platform presents a global funding posture with clear wallet records, portfolio visibility, and fast trade access.",
                "tone": "green",
            },
            {
                "label": "Business Standard",
                "title": "Built for transparent deposits, withdrawals, commissions, and trade history",
                "summary": "Every user action is reflected in the ledger, making account activity easier to audit and manage.",
                "tone": "gold",
            },
            {
                "label": "Growth Desk",
                "title": "Invite-based growth with commission tracking for every qualifying member",
                "summary": "Referral earnings, active sessions, and completed payouts stay visible without exposing staff controls.",
                "tone": "blue",
            },
        ],
        "funding_regions": [
            {"country": "USA", "label": "Private credit and retail lending market"},
            {"country": "Australia", "label": "Structured lending and savings-focused investors"},
            {"country": "United Kingdom", "label": "Digital finance and compliant capital channels"},
            {"country": "United Arab Emirates", "label": "High-liquidity commercial funding corridors"},
            {"country": "Kenya", "label": "Mobile-money-ready wallet and investor operations"},
        ],
        "quick_actions": [
            {"title": "Fund wallet", "body": "Add money before choosing a plan.", "url": "deposit"},
            {"title": "Start trading", "body": "Compare plans and begin a session.", "url": "invest"},
            {"title": "Request payout", "body": "Withdraw available approved funds.", "url": "withdraw"},
        ],
        "business_approval_note": settings.BUSINESS_APPROVAL_NOTE,
        "available_balance": totals["available_balance"],
        "total_deposits": totals["total_deposits"],
        "total_withdrawals": totals["total_withdrawals"],
        "referral_bonus": totals["referral_bonus"],
        "completed_profit": completed_profit,
        "active_capital": active_trades.aggregate(total=Sum("amount"))["total"] or 0,
    }
    return render(request, "dashboard/index.html", context)

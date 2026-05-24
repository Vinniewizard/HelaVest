from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import DepositForm, WithdrawalForm
from .models import Transaction


@login_required
def transactions(request):
    return render(request, "payments/transactions.html", {"transactions": Transaction.objects.filter(user=request.user)})


@login_required
def deposit(request):
    form = DepositForm(request.POST or None, initial={"phone": request.user.phone})
    if request.method == "POST" and form.is_valid():
        # Check for existing pending deposits
        pending_exists = Transaction.objects.filter(
            user=request.user, 
            transaction_type=Transaction.Type.DEPOSIT, 
            status=Transaction.Status.PENDING
        ).exists()
        
        if pending_exists:
            messages.error(request, "You already have a pending deposit request. Please wait for it to be approved before submitting another one.")
            return redirect("dashboard")
            
        deposit_txn = form.save(commit=False)
        deposit_txn.user = request.user
        deposit_txn.transaction_type = Transaction.Type.DEPOSIT
        deposit_txn.status = Transaction.Status.PENDING
        deposit_txn.save()
        messages.success(request, "Deposit request submitted. Funds will reflect in your wallet once verified and approved by the administrator.")
        return redirect("dashboard")
    return render(request, "payments/deposit.html", {"form": form})


@login_required
def withdraw(request):
    form = WithdrawalForm(request.POST or None, initial={"phone": request.user.phone})
    balance = Transaction.balance_for(request.user)["available_balance"]
    if request.method == "POST" and form.is_valid():
        amount = form.cleaned_data["amount"]
        if amount > balance:
            messages.error(request, "Withdrawal amount exceeds your available balance.")
            return redirect("withdraw")
        withdrawal = form.save(commit=False)
        withdrawal.user = request.user
        withdrawal.transaction_type = Transaction.Type.WITHDRAWAL
        withdrawal.status = Transaction.Status.PENDING
        withdrawal.save()
        messages.success(request, "Withdrawal request submitted for review.")
        return redirect("dashboard")
    return render(request, "payments/withdraw.html", {"form": form, "balance": balance})


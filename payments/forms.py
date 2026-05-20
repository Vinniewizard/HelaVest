from django import forms

from .models import Transaction


class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "phone", "note"]
        widgets = {"note": forms.TextInput(attrs={"placeholder": "M-Pesa code or note"})}


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "phone", "note"]
        widgets = {"note": forms.TextInput(attrs={"placeholder": "Withdrawal instructions"})}


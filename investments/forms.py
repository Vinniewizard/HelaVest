from django import forms

from .models import Plan


class InvestmentForm(forms.Form):
    plan = forms.ModelChoiceField(queryset=Plan.objects.filter(active=True), empty_label=None)


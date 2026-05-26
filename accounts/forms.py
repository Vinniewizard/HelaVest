from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=20)
    invite_code = forms.CharField(required=False, help_text="Optional invitation code")

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text to keep the form clean
        for field in self.fields.values():
            field.help_text = ""
        # Re-add specific help text for invite code if needed, but the user wants "unnecessary info" removed
        # so we'll move procedures to the template bottom.

    def clean_invite_code(self):
        code = self.cleaned_data.get("invite_code", "").strip().upper()
        if code and not User.objects.filter(referral_code=code).exists():
            raise forms.ValidationError("That invitation code was not found.")
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        code = self.cleaned_data.get("invite_code")
        if code:
            user.referred_by = User.objects.get(referral_code=code)
        if commit:
            user.save()
        return user

from django.contrib import admin

from .models import Referral


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred_user", "bonus", "created_at")
    search_fields = ("referrer__username", "referred_user__username")


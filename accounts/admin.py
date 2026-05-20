from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

admin.site.site_header = "HelaVest Administration"
admin.site.site_title = "HelaVest Admin"
admin.site.index_title = "Website management"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Investment profile", {"fields": ("phone", "referral_code", "referred_by")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Investment profile", {"fields": ("phone",)}),
    )
    list_display = ("username", "email", "phone", "referral_code", "referred_by", "is_staff")
    search_fields = ("username", "email", "phone", "referral_code")

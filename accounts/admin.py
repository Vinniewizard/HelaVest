from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User
from payments.models import Transaction

admin.site.site_header = "HelaVest Administration"
admin.site.site_title = "HelaVest Admin"
admin.site.index_title = "Website management"


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 1
    fields = ("transaction_type", "amount", "status", "note")
    classes = ("collapse",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Investment profile", {"fields": ("phone", "referral_code", "referred_by")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Investment profile", {"fields": ("phone",)}),
    )
    inlines = [TransactionInline]
    list_display = ("username", "phone", "get_balance", "quick_view", "is_active", "is_staff")
    search_fields = ("username", "email", "phone", "referral_code")
    actions = ["ban_users", "unban_users"]

    @admin.display(description="Wallet Balance")
    def get_balance(self, obj):
        balance = Transaction.balance_for(obj)["available_balance"]
        color = "green" if balance > 0 else "gray"
        return format_html('<strong style="color: {};">KSh {}</strong>', color, balance)

    @admin.action(description="Ban/Suspend selected users")
    def ban_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected users have been banned.")

    @admin.action(description="Unban/Re-enable selected users")
    def unban_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been re-enabled.")

    @admin.display(description="Quick View")
    def quick_view(self, obj):
        from django.urls import reverse
        url = reverse("admin:payments_transaction_changelist") + f"?user__id__exact={obj.id}"
        return format_html('<a href="{}" class="button" style="background: var(--primary); color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">Transactions</a>', url)

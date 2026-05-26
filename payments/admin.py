from django.contrib import admin
from django.utils.html import format_html

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "colored_type", "amount_display", "colored_status", "phone", "created_at")
    list_filter = ("transaction_type", "status", "created_at")
    search_fields = ("user__username", "user__phone", "phone", "note")
    actions = ["approve_transactions", "decline_transactions"]

    @admin.display(description="Type")
    def colored_type(self, obj):
        colors = {
            Transaction.Type.DEPOSIT: "#007a5a",
            Transaction.Type.WITHDRAWAL: "#b83232",
            Transaction.Type.INVESTMENT: "#2857c8",
            Transaction.Type.COMMISSION: "#d89b25",
            Transaction.Type.PAYOUT: "#007a5a",
        }
        color = colors.get(obj.transaction_type, "black")
        return format_html('<b style="color: {};">{}</b>', color, obj.get_transaction_type_display())

    @admin.display(description="Amount")
    def amount_display(self, obj):
        return format_html("<b>KSh {}</b>", obj.amount)

    @admin.display(description="Status")
    def colored_status(self, obj):
        colors = {
            Transaction.Status.APPROVED: "green",
            Transaction.Status.PENDING: "orange",
            Transaction.Status.DECLINED: "red",
        }
        color = colors.get(obj.status, "black")
        return format_html('<span style="background: {}; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.8rem;">{}</span>', color, obj.get_status_display().upper())

    @admin.action(description="Approve selected transactions")
    def approve_transactions(self, request, queryset):
        updated = queryset.filter(status=Transaction.Status.PENDING).update(status=Transaction.Status.APPROVED)
        self.message_user(request, f"{updated} transactions approved.")

    @admin.action(description="Decline selected transactions")
    def decline_transactions(self, request, queryset):
        updated = queryset.filter(status=Transaction.Status.PENDING).update(status=Transaction.Status.DECLINED)
        self.message_user(request, f"{updated} transactions declined.")


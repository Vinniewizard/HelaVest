from django.contrib import admin
from django.utils.html import format_html

from .models import Investment, Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "return_amount", "duration_days", "active")
    list_filter = ("active",)


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "colored_status", "created_at", "matures_at")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "user__phone")
    actions = ["complete_investments", "cancel_investments"]

    @admin.display(description="Status")
    def colored_status(self, obj):
        colors = {
            Investment.Status.ACTIVE: "#2857c8",
            Investment.Status.COMPLETED: "#007a5a",
            Investment.Status.CANCELLED: "#b83232",
        }
        color = colors.get(obj.status, "black")
        return format_html('<b style="color: {};">{}</b>', color, obj.get_status_display().upper())

    @admin.action(description="Force complete selected investments")
    def complete_investments(self, request, queryset):
        updated = queryset.filter(status=Investment.Status.ACTIVE).update(status=Investment.Status.COMPLETED)
        self.message_user(request, f"{updated} investments marked as completed.")

    @admin.action(description="Cancel selected investments")
    def cancel_investments(self, request, queryset):
        updated = queryset.filter(status=Investment.Status.ACTIVE).update(status=Investment.Status.CANCELLED)
        self.message_user(request, f"{updated} investments cancelled.")

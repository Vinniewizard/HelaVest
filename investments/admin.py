from django.contrib import admin

from .models import Investment, Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "return_amount", "duration_days", "active")
    list_filter = ("active",)


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "return_amount", "status", "created_at", "matures_at")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "user__phone")


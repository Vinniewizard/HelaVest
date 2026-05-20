from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    name = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    return_amount = models.PositiveIntegerField()
    duration_days = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ["amount"]

    @property
    def profit(self):
        return self.return_amount - self.amount

    @property
    def roi_percent(self):
        if not self.amount:
            return 0
        return round((self.profit / self.amount) * 100)

    @property
    def daily_profit(self):
        if not self.duration_days:
            return 0
        return round(self.profit / self.duration_days)

    def __str__(self):
        return f"{self.name} - KSh {self.amount}"


class Investment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()
    return_amount = models.PositiveIntegerField()
    profit = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    matures_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = self.plan.amount
        if not self.return_amount:
            self.return_amount = self.plan.return_amount
        if not self.profit:
            self.profit = self.return_amount - self.amount
        if not self.matures_at:
            self.matures_at = timezone.now() + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def days_left(self):
        remaining = self.matures_at - timezone.now()
        return max(0, remaining.days)

    @property
    def progress_percent(self):
        total_seconds = (self.matures_at - self.created_at).total_seconds()
        if total_seconds <= 0:
            return 100
        elapsed_seconds = (timezone.now() - self.created_at).total_seconds()
        return max(0, min(100, round((elapsed_seconds / total_seconds) * 100)))

    @property
    def is_matured(self):
        return self.matures_at <= timezone.now()

    def __str__(self):
        return f"{self.user} - {self.plan.name}"

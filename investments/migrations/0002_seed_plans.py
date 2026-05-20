from django.db import migrations


def seed_plans(apps, schema_editor):
    Plan = apps.get_model("investments", "Plan")
    plans = [
        {
            "name": "Starter Week",
            "amount": 1200,
            "return_amount": 1500,
            "duration_days": 7,
            "description": "Entry plan for first-time weekly trading.",
        },
        {
            "name": "Growth Week",
            "amount": 3000,
            "return_amount": 3900,
            "duration_days": 7,
            "description": "Balanced weekly plan with stronger returns.",
        },
        {
            "name": "Momentum 14",
            "amount": 7500,
            "return_amount": 10200,
            "duration_days": 14,
            "description": "Two-week session for committed investors.",
        },
        {
            "name": "Premium Month",
            "amount": 15000,
            "return_amount": 22500,
            "duration_days": 30,
            "description": "Monthly plan with premium projected payout.",
        },
    ]
    for plan in plans:
        Plan.objects.update_or_create(name=plan["name"], defaults=plan)


def remove_seed_plans(apps, schema_editor):
    Plan = apps.get_model("investments", "Plan")
    Plan.objects.filter(name__in=["Starter Week", "Growth Week", "Momentum 14", "Premium Month"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("investments", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_plans, remove_seed_plans),
    ]


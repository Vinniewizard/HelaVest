from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from investments.models import Investment, Plan
from payments.models import Transaction
from referrals.models import Referral


class InvestmentFlowTests(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(
            name="Starter Week",
            amount=1200,
            return_amount=1500,
            duration_days=7,
            active=True,
        )
        self.inviter = User.objects.create_user(
            username="inviter",
            email="inviter@example.com",
            phone="0700000001",
            password="StrongPass123",
        )

    def test_user_can_register_deposit_invest_and_generate_commission(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "member",
                "email": "member@example.com",
                "phone": "0700000002",
                "invite_code": self.inviter.referral_code,
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username="member")
        self.assertEqual(user.referred_by, self.inviter)

        self.client.post(reverse("deposit"), {"amount": 5000, "phone": user.phone, "note": "TEST"})
        self.client.post(reverse("invest"), {"plan": self.plan.id})

        self.assertEqual(Investment.objects.filter(user=user).count(), 1)
        self.assertEqual(Referral.objects.filter(referrer=self.inviter, referred_user=user).count(), 1)
        self.assertEqual(Transaction.balance_for(user)["available_balance"], 3800)
        self.assertGreater(Transaction.balance_for(self.inviter)["referral_bonus"], 0)

    def test_withdrawal_cannot_exceed_available_balance(self):
        user = User.objects.create_user(
            username="member",
            email="member@example.com",
            phone="0700000002",
            password="StrongPass123",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("withdraw"), {"amount": 1000, "phone": user.phone}, follow=True)

        self.assertContains(response, "Withdrawal amount exceeds your available balance.")
        self.assertFalse(Transaction.objects.filter(user=user, transaction_type=Transaction.Type.WITHDRAWAL).exists())

    def test_investment_workspace_and_trade_filters_render(self):
        user = User.objects.create_user(
            username="member",
            email="member@example.com",
            phone="0700000002",
            password="StrongPass123",
        )
        self.client.force_login(user)
        Transaction.objects.create(
            user=user,
            amount=5000,
            transaction_type=Transaction.Type.DEPOSIT,
            status=Transaction.Status.APPROVED,
        )

        invest_response = self.client.get(reverse("invest"))
        self.assertContains(invest_response, "Available to invest")
        self.assertContains(invest_response, "Projected profit")

        self.client.post(reverse("invest"), {"plan": self.plan.id})
        trades_response = self.client.get(f"{reverse('trades')}?status=active")

        self.assertContains(trades_response, "Active and historical trades")
        self.assertContains(trades_response, "Starter Week")
        self.assertContains(trades_response, "Progress")

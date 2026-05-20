import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models


def gen_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    referral_code = models.CharField(max_length=12, default=gen_code, unique=True)
    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals",
    )

    def __str__(self):
        return self.username


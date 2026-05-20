from django.urls import path

from .views import deposit, transactions, withdraw

urlpatterns = [
    path("", transactions, name="transactions"),
    path("deposit/", deposit, name="deposit"),
    path("withdraw/", withdraw, name="withdraw"),
]


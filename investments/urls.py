from django.urls import path

from .views import invest, trades

urlpatterns = [
    path("", trades, name="trades"),
    path("start/", invest, name="invest"),
]


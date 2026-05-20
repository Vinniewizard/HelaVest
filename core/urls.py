from django.contrib import admin
from django.urls import include, path

from accounts.views import dashboard, logout_view, register
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path("register/", register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
    path("investments/", include("investments.urls")),
    path("payments/", include("payments.urls")),
]

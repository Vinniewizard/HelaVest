from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

from accounts.views import dashboard, logout_view, register
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("management-portal/", admin.site.urls),
    path("admin/", admin.site.urls), # Fallback
    path("", dashboard, name="dashboard"),
    path("register/", register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
    path("investments/", include("investments.urls")),
    path("payments/", include("payments.urls")),
]

if settings.DEBUG or not getattr(settings, "HAS_WHITENOISE", False):
    urlpatterns += [
        re_path(r"^static/(?P<path>.*)$", static_serve, {"document_root": settings.STATICFILES_DIRS[0]}),
    ]

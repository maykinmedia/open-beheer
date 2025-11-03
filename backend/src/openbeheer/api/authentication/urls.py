from django.urls import path

from .views import EnsureCSRFTokenView, LoginView, LogoutView

app_name = "authentication"

urlpatterns = [
    path("ensure-csrf-token/", EnsureCSRFTokenView.as_view(), name="ensure-csrf-token"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

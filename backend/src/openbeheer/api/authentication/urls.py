from django.urls import path

from .views import EnsureCSRFView, LoginView, LogoutView

app_name = "authentication"

urlpatterns = [
    path("ensure-csrf/", EnsureCSRFView.as_view(), name="ensure-csrf"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

from django.urls import path

from .views import ZakenView

app_name = "authentication"

urlpatterns = [
    path("zaken/", ZakenView.as_view(), name="zaken"),
]

from django.urls import path

from .api.views import ServiceChoicesView


app_name = "services"

urlpatterns = [
    path(
        "choices/",
        ServiceChoicesView.as_view(),
        name="choices",
    ),
]

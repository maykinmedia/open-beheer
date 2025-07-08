from django.urls import path

from .api.views import CatalogChoicesView

app_name = "catalogi"

urlpatterns = [
    path(
        "choices/",
        CatalogChoicesView.as_view(),
        name="choices",
    ),
]

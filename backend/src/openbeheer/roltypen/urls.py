from django.urls import path

from .api.views import RoltypeDetailView, RoltypeListView

app_name = "api:roltypen"

urlpatterns = [
    path(
        "",
        RoltypeListView.as_view(),
        name="roltypen-list",
    ),
    path(
        "<uuid:uuid>",
        RoltypeDetailView.as_view(),
        name="roltypen-detail",
    ),
]

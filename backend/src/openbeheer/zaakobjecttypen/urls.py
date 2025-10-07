from django.urls import path

from .api.views import ZaakObjectTypeDetailView, ZaakObjectTypeListView

app_name = "api:zaakobjecttypen"

urlpatterns = [
    path(
        "",
        ZaakObjectTypeListView.as_view(),
        name="zaakobjecttypen-list",
    ),
    path(
        "<uuid:uuid>/",
        ZaakObjectTypeDetailView.as_view(),
        name="zaakobjecttypen-detail",
    ),
]

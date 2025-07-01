from django.urls import path

from .api.views import ZaakTypeDetailView, ZaakTypeListView

app_name = "api:zaaktypen"

urlpatterns = [
    path(
        "",
        ZaakTypeListView.as_view(),
        name="zaaktype-list",
    ),
    path(
        "<uuid:uuid>/",
        ZaakTypeDetailView.as_view(),
        name="zaaktype-detail",
    ),
]

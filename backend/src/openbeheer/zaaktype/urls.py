from django.urls import path

from .api.views import ZaakTypeDetailView, ZaakTypeListView

app_name = "api:zaaktypen"

urlpatterns = [
    # ZTC endpoints
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

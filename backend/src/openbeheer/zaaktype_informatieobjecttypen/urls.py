from django.urls import path

from .api.views import (
    ZaakTypeInformatieObjectTypeDetailView,
    ZaakTypeInformatieobjecttypeListView,
)

app_name = "api:zaaktype-informatieobjecttypen"

urlpatterns = [
    path(
        "",
        ZaakTypeInformatieobjecttypeListView.as_view(),
        name="zaaktype-informatieobjecttypen-list",
    ),
    path(
        "<uuid:uuid>/",
        ZaakTypeInformatieObjectTypeDetailView.as_view(),
        name="zaaktype-informatieobjecttypen-detail",
    ),
]

from django.urls import path

from .api.views import (
    InformatieObjectTypeDetailView,
    InformatieObjectTypeListView,
    InformatieObjectTypePublishView,
)

app_name = "api:informatieobjecttypen"

urlpatterns = [
    path(
        "",
        InformatieObjectTypeListView.as_view(),
        name="informatieobjecttypen-list",
    ),
    path(
        "<uuid:uuid>/",
        InformatieObjectTypeDetailView.as_view(),
        name="informatieobjecttypen-detail",
    ),
    path(
        "<uuid:uuid>/publish/",
        InformatieObjectTypePublishView.as_view(),
        name="informatieobjecttype-publish",
    ),
]

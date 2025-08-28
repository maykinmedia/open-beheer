from django.urls import path

from .api.views import BesluittypeDetailView, BesluittypeListView

app_name = "api:besluittypen"

urlpatterns = [
    path(
        "",
        BesluittypeListView.as_view(),
        name="besluittypen-list",
    ),
    path(
        "<uuid:uuid>",
        BesluittypeDetailView.as_view(),
        name="besluittypen-detail",
    ),
]

from django.urls import path

from .api.views import StatusTypeDetailView, StatusTypeListView

app_name = "api:statustypen"

urlpatterns = [
    path(
        "",
        StatusTypeListView.as_view(),
        name="statustypen-list",
    ),
    path(
        "<uuid:uuid>/",
        StatusTypeDetailView.as_view(),
        name="statustypen-detail",
    ),
]

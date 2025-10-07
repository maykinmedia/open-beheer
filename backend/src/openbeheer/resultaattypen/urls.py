from django.urls import path

from .api.views import ResultaatTypeDetailView, ResultaatTypeListView

app_name = "api:resultaattypen"

urlpatterns = [
    path(
        "",
        ResultaatTypeListView.as_view(),
        name="resultaattypen-list",
    ),
    path(
        "<uuid:uuid>/",
        ResultaatTypeDetailView.as_view(),
        name="resultaattypen-detail",
    ),
]

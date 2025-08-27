from django.urls import path

from .api.views import EigenschappenDetailView, EigenschappenListView

app_name = "api:eigenschappen"

urlpatterns = [
    path(
        "",
        EigenschappenListView.as_view(),
        name="eigenschappen-list",
    ),
    path(
        "<uuid:uuid>",
        EigenschappenDetailView.as_view(),
        name="eigenschappen-detail",
    ),
]

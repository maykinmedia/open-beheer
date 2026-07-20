from django.urls import path

from .api.views import ResultaatDetailView

app_name = "api:resultaten"

urlpatterns = [
    path(
        "",
        ResultaatDetailView.as_view(),
        name="resultaten-detail-by-url",
    ),
]

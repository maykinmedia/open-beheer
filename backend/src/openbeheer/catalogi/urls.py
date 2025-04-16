from django.urls import path

from .views import CatalogussenView

app_name = "authentication"

urlpatterns = [
    path("catalogi/", CatalogussenView.as_view(), name="catalogi"),
]

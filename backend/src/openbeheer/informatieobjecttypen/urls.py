from django.urls import path

from .api.views import InformatieObjectTypeListView

app_name = "api:informatieobjecttypen"

urlpatterns = [
    path(
        "",
        InformatieObjectTypeListView.as_view(),
        name="informatieobjecttypen-list",
    ),
]

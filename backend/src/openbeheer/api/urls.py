from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularRedocView,
)

from openbeheer.accounts.api.views import WhoAmIView
from openbeheer.health_checks.api.views import HealthChecksView
from openbeheer.zaaktype.api.views import ZaakTypeListView

app_name = "api"

urlpatterns = [
    # API documentation
    path(
        "docs/",
        SpectacularRedocView.as_view(url_name="api:api-schema-json"),
        name="api-docs",
    ),
    path(
        "v1/",
        include(
            [
                path(
                    "",
                    SpectacularJSONAPIView.as_view(schema=None),
                    name="api-schema-json",
                ),
                path("schema", SpectacularAPIView.as_view(schema=None), name="schema"),
            ]
        ),
    ),
    # Authentication
    path(
        "v1/auth/",
        include("openbeheer.api.authentication.urls", namespace="authentication"),
    ),
    # ZTC endpoints
    path(
      "v1/service/<slug:slug>/zaaktypen/",  ZaakTypeListView.as_view(), name="zaaktype-list"
    ),
    path(
      "v1/service/<slug:slug>/catalogi/",  include("openbeheer.catalogi.urls", namespace="catalogi")
    ),
    # Other endpoints
    path(
        "v1/",
        include(
            [
                path("whoami/", WhoAmIView.as_view(), name="whoami"),
                path(
                    "health-checks/", HealthChecksView.as_view(), name="health-checks"
                ),
            ]
        ),
    ),
]

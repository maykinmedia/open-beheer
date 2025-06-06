from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularRedocView,
)
from rest_framework import routers

from openbeheer.accounts.api.views import WhoAmIView
from openbeheer.health_checks.api.views import HealthChecksView
from openbeheer.zaaktype.api.views import ZaakTypeListView

router = routers.DefaultRouter()

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
    # Actual endpoints
    path(
        "v1/",
        include(
            [
                path("whoami/", WhoAmIView.as_view(), name="whoami"),
                path(
                    "health-checks/", HealthChecksView.as_view(), name="health-checks"
                ),
                path("zaaktypen/", ZaakTypeListView.as_view(), name="zaaktype-list"),
                path("", include(router.urls)),
            ]
        ),
    ),
]

from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularRedocView,
)

from openbeheer.accounts.api.views import WhoAmIView

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
            ]
        ),
    ),
]

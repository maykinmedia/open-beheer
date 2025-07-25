from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularRedocView,
)

from openbeheer.accounts.api.views import WhoAmIView
from openbeheer.health_checks.api.views import HealthChecksView
from openbeheer.zaaktype.api.views import (
    ZaakTypeTemplateListView,
    ZaakTypeTemplateView,
)

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
    # Templates
    path(
        "v1/template/zaaktype/",
        ZaakTypeTemplateListView.as_view(),
        name="zaaktypetemplate-list",
    ),
    path(
        "v1/template/zaaktype/<uuid:uuid>",
        ZaakTypeTemplateView.as_view(),
        name="zaaktypetemplate-detail",
    ),
    # ZTC endpoints
    path("v1/service/", include("openbeheer.services.urls", namespace="services")),
    path(
        "v1/service/<slug:slug>/zaaktypen/",
        include("openbeheer.zaaktype.urls", namespace="zaaktypen"),
    ),
    path(
        "v1/service/<slug:slug>/informatieobjecttypen/",
        include(
            "openbeheer.informatieobjecttypen.urls", namespace="informatieobjecttypen"
        ),
    ),
    path(
        "v1/service/<slug:slug>/catalogi/",
        include("openbeheer.catalogi.urls", namespace="catalogi"),
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

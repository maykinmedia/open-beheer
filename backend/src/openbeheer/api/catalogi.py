import logging

from django.conf import settings
from django.utils.translation import gettext as _

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response

from openbeheer.api.base.viewsets import ZGWViewSet
from openbeheer.api.oas import get_oas_spec

logger = logging.getLogger(__name__)


def get_oas_paths(oas_url: str) -> list[str]:
    """
    Retrieve the list of endpoint paths defined in the OpenAPI specification (OAS).

    Args:
        oas_url: The URL to the OpenAPI schema of the external service.

    Returns:
        A list of endpoint path strings (e.g., "/zaaktypen", "/statustypen").
    """
    spec = get_oas_spec(oas_url)
    return [p.url for p in spec.paths]


def register_catalogi(router):
    """
    Dynamically register ViewSets for ZTC resources based on the OpenAPI specification.

    This function reads the configured OAS for the ZTC service and extracts all top-level
    resource paths (e.g. 'zaaktypen', 'besluittypen', etc.). For each path, a DRF viewset
    is dynamically created and registered on the provided router, exposing standard
    `list` and `retrieve` endpoints.

    Each generated viewset:
      - Proxies requests to the configured external service using `ZGWViewSet`
      - Uses `service_api_base` to determine the endpoint
      - Is annotated with `drf-spectacular` metadata for OpenAPI schema generation

    Note:
        This registration only happens if `SERVICE_OAS` is configured. If not, no
        catalogi routes will be available.

    Args:
        router: A `rest_framework.routers.DefaultRouter` instance to register viewsets on.
    """
    if not settings.SERVICE_OAS:
        logger.warning(
            "SERVICE_OAS not configured, catalogi endpoint won't be available!"
        )
        return

    logger.info("Registering Catalogi API, this may take a while...")

    paths = get_oas_paths(settings.SERVICE_OAS)
    base_paths = [p.strip("/") for p in paths if "{" not in p]

    logger.info("Registering %s", ", ".join(base_paths))

    for path in base_paths:
        resource = path  # prevent late binding in closure

        @extend_schema(
            tags=[resource],
            description=_(
                f"Bevraagd `{resource}` via de geconfigureerde externe service."
            ),
        )
        class ViewSet(ZGWViewSet):
            """
            Dynamically generated ViewSet for a ZTC resource.

            This ViewSet is configured to proxy the operations for the given ZTC
             resource (`service_api_base`) to the external service.

            Attributes:
                service_api_base (str): The resource path to proxy (e.g. 'zaaktypen').
                service_type (str): The API type to identify the correct service.
            """

            service_api_base = resource
            service_type = settings.SERVICE_TYPE

            @extend_schema(operation_id=f"catalogi_{resource}_list")
            def list(self, *args, **kwargs) -> Response:
                """
                List all items for this resource from the external service.

                Returns:
                    Response: Paginated list of objects.
                """
                return super().list(*args, **kwargs)

            @extend_schema(
                operation_id=f"catalogi_{resource}_retrieve",
                parameters=[
                    OpenApiParameter(
                        name="uuid",
                        type=str,
                        location=OpenApiParameter.PATH,
                        description="UUID van het object",
                    )
                ],
            )
            def retrieve(self, *args, **kwargs) -> Response:
                """
                Retrieve a specific item from the external service by UUID.

                Returns:
                    Response: Serialized object if found, otherwise 404.
                """
                return super().retrieve(*args, **kwargs)

        router.register(f"catalogi/{resource}", ViewSet, basename=resource)
        logger.info("Catalogi API (%s) is registered", resource)

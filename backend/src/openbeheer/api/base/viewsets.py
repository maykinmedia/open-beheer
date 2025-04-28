from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from zgw_consumers.client import build_client, ClientT
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from .oas import get_oas_parameter_names, get_fields_from_oas_properties
from .serializers import ZGWSerializer
from .types import TypedField


class ZGWViewSet(ViewSet):
    """
    Base class for exposing ZGW data to the frontend.

    This ViewSet forwards requests to an external ZGW API using a configured service
    and maps DRF methods and actions to external API methods and paths.

    By default:
    - `get_service_method` uses the HTTP method (`GET`, `POST`, etc.) from the request.
    - `get_service_api_path` uses the DRF action name.

    Subclasses should override `get_service_method` and/or `get_service_api_path`
    if the external API uses a different method or path than DRF's.
    """

    # Fields definition (resolved if empty)
    fields: Optional[list[TypedField]]

    # ZGW Service Type.
    service_type: APITypes

    permission_classes = [IsAuthenticated]
    serializer_class = ZGWSerializer

    def get_service(self) -> Service:
        """
        Returns the configured Service instance for self.service_type.

        Raises:
            ImproperlyConfigured: If no service is configured for the given service type.
        """
        try:
            return Service.objects.filter(api_type=self.service_type).get()
        except Service.DoesNotExist:
            raise ImproperlyConfigured(
                f"No service configured for type {self.service_type}"
            )

    def get_client(self) -> ClientT:
        """
        Returns the configured Client instance for self.service_type.
        """
        return build_client(self.get_service())

    def get_service_method(self) -> str:
        """
        Returns the HTTP method (service method) to be used for the request.
        """
        return self.request.method

    def get_service_api_path(self) -> str:
        """
        Returns the API path corresponding to the DRF action name.
        """
        return self.action

    def perform_list(self) -> Response:
        """
        Fetches a list of items from the API and returns a response with the data.

        Filters request parameters to include only those supported by the service API.
        """
        service = self.get_service()
        client = self.get_client()
        method = self.get_service_method().lower()
        path = self.get_service_api_path()

        # Only proxy supported params.
        params = {
            p: self.request.query_params.get(p)
            for p in self.request.query_params
            if p in get_oas_parameter_names(service, method, path)
        }
        request = getattr(client, method)

        # Make the request to the external API
        response = request(
            path,
            params=params,
        )
        response.raise_for_status()

        resolved_fields = get_fields_from_oas_properties(self.request, service, method,
                                                         path)
        data = {
            **response.json(),
            "fields": getattr(self, "fields", resolved_fields),
        }
        serializer = self.serializer_class(instance=data, request=self.request)

        return Response(serializer.data)

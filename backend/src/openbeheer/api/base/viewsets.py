from typing import Optional

from django.core.exceptions import ImproperlyConfigured

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from zgw_consumers.client import ClientT, build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from .oas import get_fields_from_oas, get_oas_parameter_names
from .serializers import DetailZGWSerializer, ListZGWSerializer
from .types import TypedField


class ZGWViewSet(ViewSet):
    """
    Base class for exposing ZGW data to the frontend.

    This ViewSet forwards requests to an external ZGW API using a configured service
    and maps DRF methods and actions to external API methods and paths.

    By default,
    - `get_service_method` uses the HTTP method (`GET`, `POST`, etc.) from the request.
    - `get_service_api_path` uses the DRF basename.

    Subclasses should override `get_service_method` and/or `get_service_api_path`
    if the external API uses a different method or path than DRF's.
    """

    # Fields definition (resolved if empty)
    fields: Optional[list[TypedField]]

    # ZGW Service Type.
    service_type: APITypes

    lookup_field = "uuid"
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.kwargs.get("uuid"):
            return DetailZGWSerializer
        return ListZGWSerializer

    def get_service(self) -> Service:
        """
        Returns the configured Service instance for self.service_type.

        Raises:
            ImproperlyConfigured: If no service is configured for the given service type.
        """
        try:
            return Service.objects.get(api_type=self.service_type)
        except Service.DoesNotExist:
            raise ImproperlyConfigured(
                f"No service configured for type {self.service_type}"
            )
        except Service.MultipleObjectsReturned:
            raise ImproperlyConfigured(
                f"Multiple services configured for type {self.service_type}"
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
        Returns the API path corresponding to the DRF basename.
        """
        uuid = self.kwargs.get(self.lookup_field)

        if uuid:
            return self.basename + "/" + uuid.strip("/")
        return self.basename

    def get_oas_operation_path(self) -> str:
        """
        Returns the API path corresponding to the DRF basename.
        """
        uuid = self.kwargs.get(self.lookup_field)

        if uuid:
            return self.basename + "/{" + self.lookup_field + "}"
        return self.basename

    def list(self, *_, **__) -> Response:
        """
        Fetches a list of items from the API and returns a response with the data.

        Filters request parameters to include only those supported by the service API.
        """
        return self.service_request()

    def retrieve(self, *_, **__) -> Response:
        """
        Fetches an item from the API and returns a response with the data.

        Filters request parameters to include only those supported by the service API.
        """
        return self.service_request()

    def service_request(self) -> Response:
        service = self.get_service()
        client = self.get_client()
        method = self.get_service_method().lower()
        service_path = self.get_service_api_path()
        operation_path = self.get_oas_operation_path()

        # Only proxy supported params.
        params = {
            p: self.request.query_params.get(p)
            for p in self.request.query_params
            if p in get_oas_parameter_names(service, method, operation_path)
        }
        request = getattr(client, method)

        # Make the request to the external API
        response = request(
            service_path,
            params=params,
        )
        response.raise_for_status()

        resolved_fields = get_fields_from_oas(
            self.request, service, method, operation_path
        )
        data = {
            **response.json(),
            "fields": getattr(self, "fields", resolved_fields),
        }
        serializer = self.get_serializer_class()(instance=data, request=self.request)

        return Response(serializer.data)

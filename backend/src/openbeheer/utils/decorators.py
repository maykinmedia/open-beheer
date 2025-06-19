from functools import wraps
from typing import Callable
from rest_framework.response import Response
from requests.exceptions import ConnectionError

from openbeheer.types._open_beheer import ExternalServiceError


def handle_service_errors(func: Callable) -> Callable:
    """Try/except calls to external services

    Decorator to avoid crashes in case the external services (like Open Zaak or the Selectielijst API)
    are down. To be used with Views functions that request data from external services as follows:

    .. code:: python

        @handle_service_errors
        def get(request, *args, **kwargs) -> Response:
            ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Response:
        try:
            response = func(*args, **kwargs)
        except ConnectionError:
            data = ExternalServiceError(
                title="Connection error",
                detail="Could not connect to external service.",
                code="connection_error",
                status=502,
            )
            return Response(data, status=502)

        return response

    return wrapper

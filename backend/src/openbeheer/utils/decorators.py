from functools import wraps
from typing import Callable, ParamSpec
from rest_framework.response import Response
from requests.exceptions import ConnectionError, ReadTimeout

from openbeheer.types import ExternalServiceError

Params = ParamSpec("Params")


def handle_service_errors(
    func: Callable[Params, Response],
) -> Callable[Params, Response]:
    """Try/except calls to external services

    Decorator to avoid crashes in case the external services (like Open Zaak or the Selectielijst API)
    are down. To be used with Views functions that request data from external services as follows:

    .. code:: python

        @handle_service_errors
        def get(request, *args, **kwargs) -> Response:
            ...
    """

    @wraps(func)
    def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Response:
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
        except ReadTimeout:
            data = ExternalServiceError(
                title="Timeout error",
                detail="The request to the external service timed out.",
                code="timeout_error",
                status=504,
            )
            return Response(data, status=504)

        return response

    return wrapper

from django.http.response import JsonResponse

import msgspec
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import exception_handler

from openbeheer.types._zgw import ZGWError


def unauthorised_exception_handler(exc, context):
    """Custom exception handler

    Added to deal with the 401 unauthorised case in the context of session based authentication."""
    response = exception_handler(exc, context)

    if isinstance(exc, NotAuthenticated):
        response_data = ZGWError(
            title="Unauthorised",
            detail=str(exc),
            code="not_authenticated",
            instance="",
            # We return a 403, because a 401 response requires the WWW-Authenticate header with at
            # least one challenge. However, there is no value that makes sense for
            # session based authentication.
            status=status.HTTP_403_FORBIDDEN,
        )
        return JsonResponse(
            msgspec.to_builtins(response_data), status=status.HTTP_403_FORBIDDEN
        )

    return response

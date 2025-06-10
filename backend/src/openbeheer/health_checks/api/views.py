from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from ..types import HealthCheckSerialisedResult

from ..utils import run_health_checks


@extend_schema_view(
    get=extend_schema(
        tags=["Health Checks"],
        summary="Get health checks",
        description="Obtain information about whether the application is configured correctly.",
        responses={
            "200": list[HealthCheckSerialisedResult],
        },
    )
)
class HealthChecksView(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        results = run_health_checks()
        return Response(results)

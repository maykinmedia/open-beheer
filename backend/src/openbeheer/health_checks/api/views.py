from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..utils import run_health_checks


class HealthChecksView(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        results = run_health_checks()
        return Response(results)


from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response

from msgspec import Struct

class TestOption(Struct, frozen=True):
    label: str
    value: str

@extend_schema(
    responses={
        200: TestOption
    }
)
class DummyView(APIView):
    def get(self, request, format=None):
        return Response([{"label": "test", "value": "test"}])
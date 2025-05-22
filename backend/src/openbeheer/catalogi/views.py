from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response

from msgspec import Struct
import enum


class TestOption(Struct, frozen=True):
    label: str
    value: str


class OBFieldType(enum.StrEnum):
    boolean = enum.auto()
    date = enum.auto()
    daterange = enum.auto()
    null = enum.auto()
    number = enum.auto()
    string = enum.auto()
    # jsx = enum.auto()


class OBField[T](Struct, rename="camel"):
    name: str
    type: OBFieldType
    value: T | None = None


class DummyView(APIView):
    @extend_schema(responses={200: TestOption, 201: OBField})
    def get(self, request, format=None):
        return Response([{"label": "test", "value": "test"}])

    @extend_schema(request=OBField[int])
    def post(self, request, format=None):
        return Response({"name": "bla", "value": "bal", "type": "int"})

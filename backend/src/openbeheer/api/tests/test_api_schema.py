from msgspec import Struct, field
from typing import Callable
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.generators import SchemaGenerator

from openbeheer.api.views import ListView
from openbeheer.types._open_beheer import OBFieldType, OBOption
from drf_spectacular.extensions import _SchemaType


def _get_drf_spectacular_schema(view: Callable) -> _SchemaType:
    generator = SchemaGenerator()

    # drf-stubs says BaseGenerator.endpoints are just list[tuple[path, method, callback]]
    # spectacular docstring too, but code expects list[tuple[path, path_regex, method, callback]]
    generator.endpoints = [("dummy", "dummy", "GET", view)]  # type: ignore
    schema = generator.get_schema(public=True)
    return schema


class SchemaEndpointTests(APITestCase):
    def test_retrieve_json_schema(self):
        """Test that the api docs don't crash"""
        response = self.client.get(reverse("api:schema"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_msgspec_serialiser_extension(self):
        class DummyView(APIView):
            @extend_schema(
                responses={
                    200: OBOption[str],  # Generic type
                    201: OBFieldType,  # enum
                    202: OBOption,  # Msgspec struct
                    203: list[OBOption],  # list of struct
                }
            )
            def get(self, request, format=None):
                return Response()

        schema = _get_drf_spectacular_schema(DummyView.as_view())
        schemas = schema["components"]["schemas"]

        self.assertIn("OBFieldType", schemas)
        self.assertIn("OBOption", schemas)
        self.assertIn("OBOption_str_", schemas)
        self.assertIn("list_OBOption", schemas)

        self.assertIn("/dummy", schema["paths"])

        responses = schema["paths"]["/dummy"]["get"]["responses"]

        self.assertEqual(
            responses["200"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/OBOption_str_",
        )
        self.assertEqual(
            responses["201"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/OBFieldType",
        )
        self.assertEqual(
            responses["202"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/OBOption",
        )
        self.assertEqual(
            responses["203"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/list_OBOption",
        )

    def test_query_params_extension(self):
        class TestQueryParam(Struct, kw_only=True):
            some_number: int | None = None
            some_string: str = field(name="some_field", default="bla")

        class DummyView(ListView):
            query_type = TestQueryParam

            @extend_schema(filters=True)
            def get(self, request, slug: str = "") -> Response:
                return Response()

        schema = _get_drf_spectacular_schema(DummyView.as_view())
        query_parameters = schema["paths"]["/dummy"]["get"]["parameters"]

        str_query_param = query_parameters[0]

        self.assertEqual(str_query_param["name"], "some_field")
        self.assertEqual(
            str_query_param["schema"], {"type": "string", "default": "bla"}
        )

        int_query_param = query_parameters[1]

        self.assertEqual(int_query_param["name"], "some_number")
        self.assertEqual(
            int_query_param["schema"],
            {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": None},
        )

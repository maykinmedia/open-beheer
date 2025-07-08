from contextlib import redirect_stderr
from io import StringIO
from enum import Enum
from msgspec import Struct, field
from typing import Callable
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.generators import SchemaGenerator

from django.core.management import call_command

from openbeheer.api.views import ListView
from openbeheer.types import OBFieldType, OBOption
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

    def test_query_params_enums(self):
        # https://quobix.com/vacuum/rules/schemas/oas3-no-ref-siblings/

        class SomeEnum(Enum):
            a = "a"
            eh = "eh"

        class TestQueryParam(Struct, kw_only=True):
            some_enum: SomeEnum = SomeEnum.a

        class DummyView(ListView):
            query_type = TestQueryParam

            @extend_schema(filters=True)
            def get(self, request, slug: str = "") -> Response:
                return Response()

        schema = _get_drf_spectacular_schema(DummyView.as_view())
        query_parameters = schema["paths"]["/dummy"]["get"]["parameters"]

        enum_schema = query_parameters[0]["schema"]
        self.assertFalse(
            "$ref" in enum_schema and "default" in enum_schema,
            f'"default" is ignored if schema is a "$ref", both are found in {enum_schema!r}',
        )

    def test_basic_linting(self):
        # drf-spectacular should build without warnings
        # alternatively we could let these warning and error just happen and
        # write the `--file` and lint it with vacuum
        # https://quobix.com/vacuum/
        stderr = StringIO()

        # using redirect
        # call_command accepts both `stdout` *and* `stderr` params, but it does
        # nothing with the latter :thisisfine:
        with redirect_stderr(stderr):
            call_command("spectacular", ["--validate", "--file=/dev/null"])

        stderr.seek(0)
        self.assertEqual(stderr.read(), "")

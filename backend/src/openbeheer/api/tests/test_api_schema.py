from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.generators import SchemaGenerator

from openbeheer.types._open_beheer import OBFieldType, OBOption


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
                }
            )
            def get(self, request, format=None):
                return Response([{"label": "test", "value": "test"}])

        generator = SchemaGenerator()
        generator.endpoints = [("dummy", "dummy", "GET", DummyView.as_view())]
        schema = generator.get_schema(public=True)
        schemas = schema["components"]["schemas"]

        self.assertIn("OBFieldType", schemas)
        self.assertIn("OBOption", schemas)
        self.assertIn("OBOption_str_", schemas)

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

from maykin_common.vcr import VCRMixin
from msgspec import ValidationError, convert
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.types.ztc import ZaakType


class ZaakTypeTemplateListViewTest(VCRMixin, APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory.create()
        cls.url = reverse("api:zaaktypetemplate-list")

    def test_not_authenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        data = response.json()

        self.assertGreater(data["count"], 0)

        blanco = data["results"][0]

        self.assertEqual(blanco["naam"], "Blanco")
        self.assertEqual(
            blanco["omschrijving"],
            "Voor volledige vrijheid: een leeg sjabloon zonder voorgedefiniëerde structuur.",
        )

        self.assertListEqual(blanco["voorbeelden"], ["van alles", "nog wat"])

        template = data["results"][1]

        # blanco is missing all required fields
        with self.assertRaises(ValidationError):
            convert(
                blanco["waarden"] | {"catalogus": "https://example.com"},
                ZaakType,
            )

        # but this template is usable as-is
        try:
            convert(
                template["waarden"] | {"catalogus": "https://example.com"},
                ZaakType,
            )
        except ValidationError as e:
            raise self.failureException() from e

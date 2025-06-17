from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from vcr.unittest import VCRMixin
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory


class ZaakTypeListViewTest(VCRMixin, APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.service = ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
            slug="OZ",
        )
        cls.user = UserFactory.create()

    def test_not_authenticated(self):
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_zaaktype(self):
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )

        self.client.force_login(self.user)
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)

        self.assertEqual(data["result"]["identificatie"], "ZAAKTYPE-2020-0000000001")
        self.assertEqual(len(data["versions"]), 1)

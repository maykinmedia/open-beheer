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
        endpoint = reverse("api:zaaktype-list", kwargs={"slug": "OZ"})

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_list(self):
        endpoint = reverse("api:zaaktype-list", kwargs={"slug": "OZ"})

        self.client.force_login(self.user)
        response = self.client.get(endpoint)

        data = response.json()

        self.assertGreater(data["pagination"]["count"], 0)

        field_names = {f["name"] for f in data["fields"]}

        # has specced fields
        self.assertSetEqual(
            field_names,
            {
                "omschrijving",
                "identificatie",
                "eindeGeldigheid",
                "versiedatum",
                "vertrouwelijkheidaanduiding",
                "actief",
            },
        )

        # all rows have at least all fields
        for row in data["results"]:
            keys_in_fields = set(row.keys()) & field_names
            self.assertSetEqual(keys_in_fields, field_names)

    def test_catalog_filter(self):
        self.client.force_authenticate(self.user)
        url = reverse("api:zaaktype-list", kwargs={"slug": "OZ"})

        response = self.client.get(
            url, query_params={"catalogus": "ec77ad39-0954-4aeb-bcf2-1beefbadf00d"}
        )

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["pagination"]["count"], 0)
        self.assertEqual(data["results"], [])

        response = self.client.get(
            url, query_params={"catalogus": "ec77ad39-0954-4aeb-bcf2-6f45263cde77"}
        )

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(data["pagination"]["count"], 0)
        self.assertGreater(len(data["results"]), 0)

    def test_datum_geldigheid_filter(self):
        self.client.force_authenticate(self.user)
        url = reverse("api:zaaktype-list", kwargs={"slug": "OZ"})

        response = self.client.get(url, query_params={"datumGeldigheid": "2001-01-01"})

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["pagination"]["count"], 0)
        self.assertEqual(data["results"], [])

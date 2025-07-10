from furl import furl
from maykin_common.vcr import VCRMixin
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper


class InformatieObjectTypeListViewTests(VCRMixin, APITestCase):
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
        cls.endpoint = reverse(
            "api:informatieobjecttypen:informatieobjecttypen-list",
            kwargs={"slug": "OZ"},
        )
        cls.helper = OpenZaakDataCreationHelper(service_identifier="OZ")

    def test_not_authenticated(self):
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_informatieobjecttypen(self):
        self.helper.create_informatieobjecttype()

        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertGreater(data["pagination"]["count"], 1)

    def test_retrieve_with_filter_catalogus(self):
        catalogus = self.helper.create_catalogus()
        assert catalogus.url
        self.helper.create_informatieobjecttype(
            overrides={
                "catalogus": catalogus.url,
                "omschrijving": "test_retrieve_with_filter_catalogus 1",
            }
        )
        self.helper.create_informatieobjecttype(
            overrides={
                "omschrijving": "test_retrieve_with_filter_catalogus 2",
            }
        )

        self.client.force_login(self.user)
        # Without filter
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertGreater(data["pagination"]["count"], 2)

        # With filter
        catalogus_uuid = furl(catalogus.url).path.segments[-1]
        response = self.client.get(
            self.endpoint,
            query_params={"catalogus": catalogus_uuid, "status": "concept"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["pagination"]["count"], 1)
        self.assertEqual(
            "test_retrieve_with_filter_catalogus 1", data["results"][0]["omschrijving"]
        )

    def test_retrieve_with_filter_zaaktype(self):
        """Make some informatieobjecttypen that are related to a zaaktype.
        Then test filtering on zaaktype."""
        zaaktype = self.helper.create_zaaktype()

        iot1 = self.helper.create_informatieobjecttype(
            overrides={
                "omschrijving": "test_retrieve_with_filter_zaaktype 1",
                "catalogus": zaaktype.catalogus,
            }
        )
        iot2 = self.helper.create_informatieobjecttype(
            overrides={"omschrijving": "test_retrieve_with_filter_zaaktype 2"}
        )

        assert zaaktype.url and iot1.url and iot2.url

        self.helper.relate_zaaktype_informatieobjecttype(
            zaaktype.url, iot1.url, overrides={"volgnummer": 1}
        )

        # Without Filtering
        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertGreater(data["pagination"]["count"], 1)

        # With Filtering
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]
        response = self.client.get(
            self.endpoint, query_params={"zaaktype": zaaktype_uuid, "status": "concept"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["pagination"]["count"], 1)
        self.assertEqual(
            "test_retrieve_with_filter_zaaktype 1", data["results"][0]["omschrijving"]
        )

    def test_create(self):
        catalogus = self.helper.create_catalogus()
        assert catalogus.url

        self.client.force_login(self.user)
        response = self.client.post(
            self.endpoint,
            data={
                "catalogus": catalogus.url,
                "omschrijving": "Testing IOT",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2025-07-10",
                "informatieobjectcategorie": "no idea what this should be ¯\\_(ツ)_/¯",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

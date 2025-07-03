from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory
from maykin_common.vcr import VCRMixin

from openbeheer.accounts.tests.factories import UserFactory
from furl import furl

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

        field_names = {f["name"] for f in data["fields"]}

        # has specced fields
        self.assertSetEqual(
            field_names,
            {
                "url",
                "omschrijving",
                "vertrouwelijkheidaanduiding",
                "actief",
                "eindeGeldigheid",
                "concept",
            },
        )

    def test_retrieve_with_filter_catalogus(self):
        catalogus1 = self.helper.create_catalogus()
        catalogus2 = self.helper.create_catalogus()
        self.helper.create_informatieobjecttype(
            overrides={
                "catalogus": catalogus1.url,
                "omschrijving": "test_retrieve_with_filter_catalogus 1",
            }
        )
        self.helper.create_informatieobjecttype(
            overrides={
                "catalogus": catalogus1.url,
                "omschrijving": "test_retrieve_with_filter_catalogus 2",
            }
        )
        self.helper.create_informatieobjecttype(
            overrides={
                "catalogus": catalogus2.url,
                "omschrijving": "test_retrieve_with_filter_catalogus 3",
            }
        )

        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertGreater(data["pagination"]["count"], 2)

        omschrijvingen = [iot["omschrijving"] for iot in data["results"]]

        self.assertIn("test_retrieve_with_filter_catalogus 1", omschrijvingen)
        self.assertIn("test_retrieve_with_filter_catalogus 2", omschrijvingen)

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
            overrides={
                "omschrijving": "test_retrieve_with_filter_zaaktype 2",
                "catalogus": zaaktype.catalogus,
            }
        )
        self.helper.create_informatieobjecttype(
            overrides={
                "omschrijving": "test_retrieve_with_filter_zaaktype 3",
                "catalogus": zaaktype.catalogus,
            }
        )

        assert zaaktype.url and iot1.url and iot2.url

        self.helper.relate_zaaktype_informatieobjecttype(
            zaaktype.url,
            iot1.url,
            overrides={"volgnummer": 1},
        )
        self.helper.relate_zaaktype_informatieobjecttype(
            zaaktype.url,
            iot2.url,
            overrides={"volgnummer": 2},
        )

        # Without Filtering
        catalogus_uuid = furl(zaaktype.catalogus).path.segments[-1]
        self.client.force_login(self.user)
        response = self.client.get(
            self.endpoint,
            query_params={"catalogus": catalogus_uuid, "status": "concept"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["pagination"]["count"], 3)

        # With Filtering
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]
        response = self.client.get(
            self.endpoint,
            query_params={
                "catalogus": catalogus_uuid,
                "zaaktype": zaaktype_uuid,
                "status": "concept",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["pagination"]["count"], 2)

        omschrijvingen = [iot["omschrijving"] for iot in data["results"]]

        self.assertIn("test_retrieve_with_filter_zaaktype 1", omschrijvingen)
        self.assertIn("test_retrieve_with_filter_zaaktype 2", omschrijvingen)

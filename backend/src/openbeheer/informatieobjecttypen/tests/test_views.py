from msgspec.json import decode
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory
from maykin_common.vcr import VCRMixin

from openbeheer.clients import ztc_client
from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.types.ztc import (
    Catalogus,
    InformatieObjectType,
    ZaakType,
    ZaakTypeInformatieObjectType,
)
from furl import furl

# TODO: Make a separate mixin helper for creating the OZ resources
# TODO: Improve the types of the helper functions
# TODO: record cassettes
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

    def _create_informatieobjecttype(self, overrides: dict | None = None):
        data = {
            "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
            "omschrijving": "Omschrijving A",
            "vertrouwelijkheidaanduiding": "openbaar",
            "beginGeldigheid": "2025-07-01",
            "informatieobjectcategorie": "Blue",
        }
        if overrides:
            data.update(overrides)

        with ztc_client("OZ") as client:
            response = client.post("informatieobjecttypen", json=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return decode(
            response.content,
            type=InformatieObjectType,
            strict=False,
        )

    def _create_catalogus(self, overrides: dict | None = None):
        data = {
            "domein": "AAAAAA",
            "rsin": "123456782",
            "contactpersoonBeheerNaam": "Ubaldo",
        }
        if overrides:
            data.update(overrides)

        with ztc_client("OZ") as client:
            response = client.post("catalogussen", json=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return decode(
            response.content,
            type=Catalogus,
            strict=False,
        )

    def _relate_zaaktype_informatieobjecttype(
        self,
        zaaktype_url: str,
        informatieobjecttype_url: str,
        overrides: dict | None = None,
    ) -> ZaakTypeInformatieObjectType:
        data = {
            "zaaktype": zaaktype_url,
            "informatieobjecttype": informatieobjecttype_url,
            "volgnummer": 1,
            "richting": "inkomend",
        }
        if overrides:
            data.update(overrides)

        with ztc_client("OZ") as client:
            response = client.post("zaaktype-informatieobjecttypen", json=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return decode(
            response.content,
            type=ZaakTypeInformatieObjectType,
            strict=False,
        )

    def _create_zaaktype(self, overrides: dict | None = None):
        data = {
            "omschrijving": "Another test zaaktype",
            "vertrouwelijkheidaanduiding": "geheim",
            "doel": "New Zaaktype 001",
            "aanleiding": "New Zaaktype 001",
            "indicatieInternOfExtern": "intern",
            "handelingInitiator": "aanvragen",
            "onderwerp": "New Zaaktype 001",
            "handelingBehandelaar": "handelin",
            "doorlooptijd": "P40D",
            "opschortingEnAanhoudingMogelijk": False,
            "verlengingMogelijk": True,
            "verlengingstermijn": "P40D",
            "publicatieIndicatie": False,
            "productenOfDiensten": ["https://example.com/product/321"],
            "referentieproces": {"naam": "ReferentieProces 1"},
            "verantwoordelijke": "200000000",
            "beginGeldigheid": "2025-06-19",
            "versiedatum": "2025-06-19",
            "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
            "besluittypen": [],
            "gerelateerdeZaaktypen": [],
        }
        if overrides:
            data.update(overrides)

        with ztc_client("OZ") as client:
            response = client.post("zaaktypen", json=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return decode(
            response.content,
            type=ZaakType,
            strict=False,
        )

    def test_not_authenticated(self):
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_informatieobjecttypen(self):
        self._create_informatieobjecttype()

        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertGreater(data["pagination"]["count"], 1)

    def test_retrieve_with_filter_catalogus(self):
        catalogus = self._create_catalogus(overrides={"domein": "OAOAO"})
        self._create_informatieobjecttype(
            overrides={
                "catalogus": catalogus.url,
                "omschrijving": "test_retrieve_with_filter_catalogus 1",
            }
        )
        self._create_informatieobjecttype(
            overrides={
                "catalogus": catalogus.url,
                "omschrijving": "test_retrieve_with_filter_catalogus 2",
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
        zaaktype = self._create_zaaktype()

        iot1 = self._create_informatieobjecttype(
            overrides={"omschrijving": "test_retrieve_with_filter_zaaktype 1"}
        )
        iot2 = self._create_informatieobjecttype(
            overrides={"omschrijving": "test_retrieve_with_filter_zaaktype 2"}
        )

        assert zaaktype.url and iot1.url and iot2.url

        self._relate_zaaktype_informatieobjecttype(zaaktype.url, iot1.url, overrides={"volgnummer":1})
        self._relate_zaaktype_informatieobjecttype(zaaktype.url, iot2.url, overrides={"volgnummer":2})

        # Without Filtering
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertGreater(data["pagination"]["count"], 2)

        # With Filtering
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]
        response = self.client.get(
            self.endpoint, params={"zaaktype": zaaktype_uuid, "status": "concept"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["pagination"]["count"], 2)

        omschrijvingen = [iot["omschrijving"] for iot in data["results"]]

        self.assertIn("test_retrieve_with_filter_zaaktype 1", omschrijvingen)
        self.assertIn("test_retrieve_with_filter_zaaktype 2", omschrijvingen)

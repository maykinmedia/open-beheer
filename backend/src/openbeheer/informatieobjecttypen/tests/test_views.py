from furl import furl
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import VCRAPITestCase


class InformatieObjectTypeListViewTests(VCRAPITestCase):
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
        cls.helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

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
            catalogus=catalogus.url,
            omschrijving="test_retrieve_with_filter_catalogus 1",
        )
        self.helper.create_informatieobjecttype(
            omschrijving="test_retrieve_with_filter_catalogus 2",
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
            omschrijving="test_retrieve_with_filter_zaaktype 1",
            catalogus=zaaktype.catalogus,
        )
        iot2 = self.helper.create_informatieobjecttype(
            omschrijving="test_retrieve_with_filter_zaaktype 2"
        )

        assert zaaktype.url and iot1.url and iot2.url

        self.helper.relate_zaaktype_informatieobjecttype(
            zaaktype.url, iot1.url, volgnummer=1
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


class InformatieObjectTypeDetailViewTest(VCRAPITestCase):
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

        cls.helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        endpoint = reverse(
            "api:informatieobjecttypen:informatieobjecttypen-detail",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_informatieobjecttype(self):
        iot = self.helper.create_informatieobjecttype()

        assert iot.url
        iot_uuid = furl(iot.url).path.segments[-1]
        self.client.force_login(self.user)

        endpoint = reverse(
            "api:informatieobjecttypen:informatieobjecttypen-detail",
            kwargs={"slug": "OZ", "uuid": iot_uuid},
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertNotIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)
        self.assertIn("fields", data)

        fields = {f["name"] for f in data["fields"]}

        self.assertSetEqual(fields, set(data["result"].keys()))

        iot_data = data["result"]

        with self.subTest("result"):
            self.assertIn("url", iot_data)
            self.assertIn("omschrijving", iot_data)
            self.assertIn("catalogus", iot_data)
            self.assertIn("vertrouwelijkheidaanduiding", iot_data)
            self.assertIn("beginGeldigheid", iot_data)
            self.assertIn("eindeGeldigheid", iot_data)
            self.assertIn("concept", iot_data)
            self.assertIn("trefwoord", iot_data)
            self.assertIn("omschrijvingGeneriek", iot_data)
            self.assertIn("zaaktypen", iot_data)
            self.assertIn("beginObject", iot_data)
            self.assertIn("eindeObject", iot_data)

        with self.subTest("expand"):
            self.assertNotIn("_expand", iot_data)

        with self.subTest("fields"):
            self.assertEqual(data["fields"][2]["name"], "vertrouwelijkheidaanduiding")
            self.assertEqual(len(data["fields"][2]["options"]), 8)

    def test_patch_informatieobjecttype(self):
        iot = self.helper.create_informatieobjecttype()

        assert iot.url
        iot_uuid = furl(iot.url).path.segments[-1]
        self.client.force_login(self.user)

        endpoint = reverse(
            "api:informatieobjecttypen:informatieobjecttypen-detail",
            kwargs={"slug": "OZ", "uuid": iot_uuid},
        )

        # Now modify the iot
        self.client.force_login(self.user)

        response = self.client.patch(
            endpoint,
            data={"omschrijving": "MODIFIED by test test_patch_informatieobjecttype"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertNotIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)

        with self.subTest("Modified field"):
            self.assertEqual(
                data["result"]["omschrijving"],
                "MODIFIED by test test_patch_informatieobjecttype",
            )

    def test_put_informatieobjecttype(self):
        iot = self.helper.create_informatieobjecttype()

        assert iot.url
        iot_uuid = furl(iot.url).path.segments[-1]
        self.client.force_login(self.user)

        endpoint = reverse(
            "api:informatieobjecttypen:informatieobjecttypen-detail",
            kwargs={"slug": "OZ", "uuid": iot_uuid},
        )

        # Now modify the iot
        self.client.force_login(self.user)

        response = self.client.put(
            endpoint,
            data={
                "omschrijving": "MODIFIED by test test_put_informatieobjecttype",
                "catalogus": iot.catalogus,
                "vertrouwelijkheidaanduiding": "geheim",
                "beginGeldigheid": "2025-07-10",
                "eindeGeldigheid": "2030-07-10",
                "concept": True,
                "trefwoord": ["MODIFIED"],
                "informatieobjectcategorie": "MODIFIED",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertNotIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)

        iot_data = data["result"]

        # Now check the modified values
        self.assertEqual(
            iot_data["omschrijving"], "MODIFIED by test test_put_informatieobjecttype"
        )
        self.assertTrue(iot_data["concept"])
        self.assertEqual(iot_data["vertrouwelijkheidaanduiding"], "geheim")
        self.assertEqual(iot_data["catalogus"], iot_data["catalogus"])
        self.assertEqual(iot_data["beginGeldigheid"], "2025-07-10")
        self.assertEqual(iot_data["eindeGeldigheid"], "2030-07-10")
        self.assertEqual(iot_data["trefwoord"], ["MODIFIED"])
        self.assertEqual(iot_data["informatieobjectcategorie"], "MODIFIED")

    def test_delete_informatieobjecttype(self):
        iot = self.helper.create_informatieobjecttype()

        assert iot.url
        iot_uuid = furl(iot.url).path.segments[-1]
        self.client.force_login(self.user)

        endpoint = reverse(
            "api:informatieobjecttypen:informatieobjecttypen-detail",
            kwargs={"slug": "OZ", "uuid": iot_uuid},
        )

        # Now modify the iot
        self.client.force_login(self.user)

        response = self.client.delete(endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

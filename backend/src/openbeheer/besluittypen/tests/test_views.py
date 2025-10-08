from msgspec import to_builtins
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.clients import ztc_client
from openbeheer.types.ztc import VertrouwelijkheidaanduidingEnum
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import VCRAPITestCase


class BesluitTypeListViewTests(VCRAPITestCase):
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

    def setUp(self):
        super().setUp()
        # create a fresh zaaktype and set its besluittype endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        self.endpoint = reverse(
            "api:besluittypen:besluittypen-list",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
            },
        )

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_besluittypen(self):
        # Frontend uses _expand instead, but this works too

        assert self.zaaktype.url
        besluittype = self.helper.create_besluittype(
            zaaktype=self.zaaktype.url, catalogus=self.zaaktype.catalogus
        )

        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertGreaterEqual(data["pagination"]["count"], 1)
        created = to_builtins(besluittype)
        self.assertEqual(data["results"][0], created)

    def test_create(self):
        "Create a new besluittype for a zaaktype"
        self.client.force_login(self.user)

        response = self.client.post(
            self.endpoint,
            data={
                "catalogus": self.zaaktype.catalogus,
                "publicatieIndicatie": True,
                "informatieobjecttypen": [],
                "beginGeldigheid": "2025-06-19",
                "omschrijving": "Tja",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["omschrijving"], "Tja")

        # this is what we put in the response
        self.assertIn(self.zaaktype.url, data["zaaktypen"])

        # double check if OZ agrees with our state
        refreshed = ztc_client("OZ").get(data["url"]).json()
        self.assertIn(self.zaaktype.url, refreshed["zaaktypen"])

        assert self.cassette
        # we shouldn't have sent snake_case to the service
        # OZ might work, but other implementations may not
        requests_to_service = (
            r for r in self.cassette.requests if r.uri.startswith(self.service.api_root)
        )
        requests_with_snake_case = [
            (r, r.body)
            for r in requests_to_service
            if r.body
            and any(
                snake_case in r.body
                for snake_case in [b"begin_geldigheid", b"publicatie_indicatie"]
            )
        ]

        assert requests_with_snake_case == []


class BesluitTypeDetailViewTest(VCRAPITestCase):
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

    def setUp(self):
        super().setUp()
        # create a fresh besluittype and set its endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        assert self.zaaktype.url
        self.besluittype = self.helper.create_besluittype(
            catalogus=self.zaaktype.catalogus
        )
        # add it to the zaaktype
        with ztc_client("OZ") as client:
            patched = client.patch(
                self.zaaktype.url,
                json={
                    "besluittypen": self.zaaktype.besluittypen + [self.besluittype.url]
                },
            )
        assert patched.ok, patched.json()

        self.besluittype.zaaktypen = [self.zaaktype.url] + (
            self.besluittype.zaaktypen or []
        )

        self.endpoint = reverse(
            "api:besluittypen:besluittypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
                "uuid": self.besluittype.uuid,
            },
        )

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_besluittype(self):
        self.client.force_login(self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        result_keys = set(data.keys())
        assert result_keys == {
            "beginGeldigheid",
            "beginObject",
            "besluitcategorie",
            "catalogus",
            "concept",
            "eindeGeldigheid",
            "eindeObject",
            "informatieobjecttypen",
            "omschrijving",
            "omschrijvingGeneriek",
            "publicatieIndicatie",
            "publicatietekst",
            "publicatietermijn",
            "reactietermijn",
            "resultaattypen",
            "resultaattypenOmschrijving",
            "toelichting",
            "url",
            "vastgelegdIn",
            "zaaktypen",
        }

        self.assertIn(self.zaaktype.url, data["zaaktypen"])

    def test_patch_besluittype(self):
        self.client.force_login(self.user)

        changes = {"omschrijving": "MODIFIED by patch"}

        response = self.client.patch(self.endpoint, data=changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()

        expected = to_builtins(self.besluittype) | changes

        del expected["uuid"]

        assert data == expected

        self.assertEqual(data, expected)

    def test_put_besluittype(self):
        self.client.force_login(self.user)

        response = self.client.put(
            self.endpoint,
            data={
                "zaaktypen": [self.zaaktype.url],
                "catalogus": self.zaaktype.catalogus,
                "omschrijving": "PUTjeschepper",
                "publicatieIndicatie": True,
                "informatieobjecttypen": [],
                "beginGeldigheid": "2025-06-19",
                "concept": False,  #  ignored, should use POST to /publish
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["omschrijving"], "PUTjeschepper")
        self.assertIn(self.zaaktype.url, data["zaaktypen"])
        self.assertEqual(data["concept"], True)

    def test_delete_besluittype(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

from msgspec import to_builtins
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.types.ztc import FormaatEnum, VertrouwelijkheidaanduidingEnum
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import VCRAPITestCase


class EigenschappenListViewTests(VCRAPITestCase):
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
        # create a fresh zaaktype and set its eigenschappen endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        self.endpoint = reverse(
            "api:eigenschappen:eigenschappen-list",
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

    def test_retrieve_eigenschappen(self):
        # Frontend uses _expand instead, but this works too

        assert self.zaaktype.url
        eigenschap = self.helper.create_eigenschap(zaaktype=self.zaaktype.url)

        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["pagination"]["count"], 1)
        created = to_builtins(eigenschap)
        self.assertEqual(data["results"][0], created)

    def test_create(self):
        "Create a new eigenschappen for a zaaktype"
        self.skipTest("API diverged")
        self.client.force_login(self.user)
        response = self.client.post(
            self.endpoint,
            data={
                "naam": "Piet",
                "definitie": "Ook niet de broer van Henk de Vries",
                "specificatie": {
                    "formaat": "getal",
                    "lengte": "64",
                    "kardinaliteit": "N",
                    "groep": "",
                    "waardenverzameling": [],
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

    def test_patched_create(self):
        "Create a new eigenschappen for a zaaktype"
        self.client.force_login(self.user)

        for n, formaat in enumerate(FormaatEnum):
            with self.subTest(f"Creating {formaat}"):
                response = self.client.post(
                    self.endpoint,
                    data={
                        "naam": f"Piet {n}",
                        "definitie": "Ook niet de broer van Henk de Vries",
                        "formaat": formaat.value,
                    },
                    format="json",
                )
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, response.json()
            )

    def test_oversized_definitie(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.endpoint,
            data={
                "naam": "Zeg 'ns",
                "definitie": "A" * 256,
                "formaat": "datum",
            },
            format="json",
        )
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, json)

        self.assertEqual(json["invalidParams"][0]["name"], "definitie")


class EigenschappenDetailViewTest(VCRAPITestCase):
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
        # create a fresh eigenschappen and set its endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        assert self.zaaktype.url
        self.eigenschappen = self.helper.create_eigenschap(zaaktype=self.zaaktype.url)

        self.endpoint = reverse(
            "api:eigenschappen:eigenschappen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
                "uuid": self.eigenschappen.uuid,
            },
        )

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_eigenschappen(self):
        self.client.force_login(self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        result_keys = set(data.keys())
        assert result_keys == {
            "beginGeldigheid",
            "beginObject",
            "catalogus",
            "definitie",
            "eindeGeldigheid",
            "eindeObject",
            "naam",
            "specificatie",
            "statustype",
            "toelichting",
            "url",
            "zaaktype",
            "zaaktypeIdentificatie",
            "adminUrl",
            "uuid",
            "formaat",
        }

    def test_patch_eigenschappen(self):
        self.client.force_login(self.user)

        changes = {"naam": "MODIFIED by patch"}

        response = self.client.patch(self.endpoint, data=changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()

        expected = to_builtins(self.eigenschappen) | changes

        assert data == expected

    def test_put_eigenschappen(self):
        self.client.force_login(self.user)

        response = self.client.put(
            self.endpoint,
            data={
                "zaaktype": self.zaaktype.url,
                "naam": "PUTjeschepper",
                "definitie": "Ook niet de broer van Henk de Vries",
                "formaat": "getal",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()

        self.assertEqual(data["zaaktype"], self.zaaktype.url)
        self.assertEqual(data["naam"], "PUTjeschepper")

    def test_delete_eigenschappen(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_oversized_definitie(self):
        self.client.force_login(self.user)

        response = self.client.put(
            self.endpoint,
            data={
                "naam": "Zeg 'ns",
                "definitie": "A" * 256,
                "formaat": "datum",
            },
            format="json",
        )
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, json)

        self.assertEqual(json["invalidParams"][0]["name"], "definitie")

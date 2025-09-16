from msgspec import to_builtins
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.types.ztc import VertrouwelijkheidaanduidingEnum
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import VCRAPITestCase


class RoltypeListViewTests(VCRAPITestCase):
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
        # create a fresh zaaktype and set its roltype endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        self.endpoint = reverse(
            "api:roltypen:roltypen-list",
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

    def test_retrieve_roltypen(self):
        # Frontend uses _expand instead, but this works too

        assert self.zaaktype.url
        roltype = self.helper.create_roltype(zaaktype=self.zaaktype.url)

        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["pagination"]["count"], 1)
        created = to_builtins(roltype)
        self.assertEqual(data["results"][0], created)

    def test_create(self):
        "Create a new roltype for a zaaktype"
        self.client.force_login(self.user)
        response = self.client.post(
            self.endpoint,
            data={
                "omschrijving": "Vernieuwde receptuur",
                "omschrijvingGeneriek": "klantcontacter",  # lekker genederlandst
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["zaaktype"], self.zaaktype.url)


class RoltypeDetailViewTest(VCRAPITestCase):
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
        # create a fresh roltype and set its endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        assert self.zaaktype.url
        self.roltype = self.helper.create_roltype(zaaktype=self.zaaktype.url)

        self.endpoint = reverse(
            "api:roltypen:roltypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
                "uuid": self.roltype.uuid,
            },
        )

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_roltype(self):
        self.client.force_login(self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        result_keys = set(data.keys())
        assert result_keys == {
            "beginGeldigheid",
            "beginObject",
            "catalogus",
            "eindeGeldigheid",
            "eindeObject",
            "omschrijving",
            "omschrijvingGeneriek",
            "url",
            "uuid",  # our adition
            "zaaktype",
            "zaaktypeIdentificatie",
        }

    def test_patch_roltype(self):
        self.client.force_login(self.user)

        changes = {"omschrijving": "MODIFIED by patch"}

        response = self.client.patch(self.endpoint, data=changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()

        expected = to_builtins(self.roltype) | changes

        self.assertEqual(data, expected)

    def test_put_roltype(self):
        self.client.force_login(self.user)

        response = self.client.put(
            self.endpoint,
            data={
                "zaaktype": self.zaaktype.url,
                "omschrijving": "PUTjeschepper",
                "omschrijvingGeneriek": "klantcontacter",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()

        self.assertEqual(data["zaaktype"], self.zaaktype.url)
        self.assertEqual(data["omschrijving"], "PUTjeschepper")

    def test_delete_roltype(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

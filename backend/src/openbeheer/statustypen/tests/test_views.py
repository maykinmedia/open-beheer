from msgspec import to_builtins
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.types.ztc import VertrouwelijkheidaanduidingEnum
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import VCRAPITestCase


class StatusTypeListViewTests(VCRAPITestCase):
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
        cls.helper = OpenZaakDataCreationHelper(service_identifier="OZ")

    def setUp(self):
        super().setUp()
        # create a fresh zaaktype and set its statustype endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        self.endpoint = reverse(
            "api:statustypen:statustypen-list",
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

    def test_retrieve_statustypen(self):
        # Frontend uses _expand instead, but this works too

        assert self.zaaktype.url
        statustype = self.helper.create_statustype(zaaktype=self.zaaktype.url)

        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["pagination"]["count"], 1)
        created = to_builtins(statustype)
        self.assertEqual(data["results"][0], created)

    def test_create(self):
        "Create a new statustype for a zaaktype"
        self.client.force_login(self.user)
        response = self.client.post(
            self.endpoint,
            data={
                "omschrijving": "Vernieuwde receptuur",
                "volgnummer": 1,
                "omschrijving_generiek": "",
                "statustekst": "",
                "informeren": False,
                "checklistitem_statustype": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class StatusTypeDetailViewTest(VCRAPITestCase):
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

        cls.helper = OpenZaakDataCreationHelper(service_identifier="OZ")

    def setUp(self):
        super().setUp()
        # create a fresh statustype and set its endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        assert self.zaaktype.url
        self.statustype = self.helper.create_statustype(zaaktype=self.zaaktype.url)

        self.endpoint = reverse(
            "api:statustypen:statustypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
                "uuid": self.statustype.uuid,
            },
        )

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_statustype(self):
        self.client.force_login(self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        result_keys = set(data.keys())
        assert result_keys == {
            "beginGeldigheid",
            "beginObject",
            "catalogus",
            "checklistitemStatustype",
            "doorlooptijd",
            "eigenschappen",
            "eindeGeldigheid",
            "eindeObject",
            "informeren",
            "isEindstatus",
            "omschrijving",
            "omschrijvingGeneriek",
            "statustekst",
            "toelichting",
            "url",
            "volgnummer",
            "zaakobjecttypen",
            "zaaktype",
            "zaaktypeIdentificatie",
        }

    def test_patch_statustype(self):
        self.client.force_login(self.user)

        changes = {"omschrijving": "MODIFIED by patch"}

        response = self.client.patch(self.endpoint, data=changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()

        expected = to_builtins(self.statustype) | changes

        del expected["uuid"]

        self.assertEqual(data, expected)

    def test_put_statustype(self):
        self.client.force_login(self.user)

        response = self.client.put(
            self.endpoint,
            data={
                "omschrijving": "PUTjeschepper",
                "volgnummer": 1,
                "omschrijving_generiek": "",
                "statustekst": "",
                "informeren": False,
                "checklistitem_statustype": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["zaaktype"], self.zaaktype.url)
        self.assertEqual(data["omschrijving"], "PUTjeschepper")
        self.assertEqual(data["volgnummer"], 1)
        self.assertEqual(data["omschrijvingGeneriek"], "")
        self.assertEqual(data["statustekst"], "")
        self.assertEqual(data["informeren"], False)
        self.assertEqual(data["checklistitemStatustype"], [])

    def test_delete_statustype(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

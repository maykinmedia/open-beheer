from msgspec import to_builtins
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.clients import ztc_client
from openbeheer.config.tests.factories import APIConfigFactory
from openbeheer.types.ztc import VertrouwelijkheidaanduidingEnum
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import VCRAPITestCase


class ZaakObjectTypeListViewTests(VCRAPITestCase):
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
        APIConfigFactory.create()
        cls.user = UserFactory.create()
        cls.helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")

    def setUp(self):
        super().setUp()
        # create a fresh zaaktype and set its zaakobjecttype endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        self.endpoint = reverse(
            "api:zaakobjecttypen:zaakobjecttypen-list",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
            },
        )
        # also create requirements to publish:
        assert self.zaaktype.url
        self.helper.create_roltype(zaaktype=self.zaaktype.url)
        self.helper.create_resultaattype(zaaktype=self.zaaktype.url)

        self.helper.create_statustype(
            zaaktype=self.zaaktype.url,
            omschrijving="begin",
            volgnummer=1,
        )
        self.helper.create_statustype(
            zaaktype=self.zaaktype.url,
            omschrijving="eind",
            volgnummer=2,
        )

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_zaakobjecttypen(self):
        # Frontend uses _expand instead, but this works too

        assert self.zaaktype.url
        zaakobjecttype = self.helper.create_zaakobjecttype(zaaktype=self.zaaktype.url)

        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # 🎱: "My sources say no"
        # OZ zot list only lists zots of published zaken...
        # This is not clear to me from the VNG spec runtime notations:
        # https://vng-realisatie.github.io/gemma-zaken/standaard/catalogi/
        self.assertEqual(data["pagination"]["count"], 0)

        with ztc_client("OZ") as client:
            assert client.post(f"{self.zaaktype.url}/publish").ok

        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["pagination"]["count"], 1)
        created = to_builtins(zaakobjecttype)
        self.assertEqual(data["results"][0], created)

    def test_create(self):
        "Create a new zaakobjecttype for a zaaktype"
        self.client.force_login(self.user)
        response = self.client.post(
            self.endpoint,
            data={
                "anderObjecttype": False,
                "objecttype": "https://example.com",
                "relatieOmschrijving": "LAT",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["zaaktype"], self.zaaktype.url)


class ZaakObjectTypeDetailViewTest(VCRAPITestCase):
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
        APIConfigFactory.create()
        cls.user = UserFactory.create()

        cls.helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")

    def setUp(self):
        super().setUp()
        # create a fresh zaakobjecttype and set its endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        assert self.zaaktype.url
        self.zaakobjecttype = self.helper.create_zaakobjecttype(
            zaaktype=self.zaaktype.url
        )

        self.endpoint = reverse(
            "api:zaakobjecttypen:zaakobjecttypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
                "uuid": self.zaakobjecttype.uuid,
            },
        )

        # also create requirements to publish:
        assert self.zaaktype.url
        self.helper.create_roltype(zaaktype=self.zaaktype.url)
        self.helper.create_resultaattype(zaaktype=self.zaaktype.url)

        self.helper.create_statustype(
            zaaktype=self.zaaktype.url,
            omschrijving="begin",
            volgnummer=1,
        )
        self.helper.create_statustype(
            zaaktype=self.zaaktype.url,
            omschrijving="eind",
            volgnummer=2,
        )

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_zaakobjecttype(self):
        self.client.force_login(self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        result_keys = set(data.keys())

        assert result_keys == {
            "anderObjecttype",
            "beginGeldigheid",
            "beginObject",
            "catalogus",
            "eindeGeldigheid",
            "eindeObject",
            "objecttype",
            "relatieOmschrijving",
            "resultaattypen",
            "statustype",
            "url",
            "zaaktype",
            "zaaktypeIdentificatie",
            "_expand",
            "uuid",
            "adminUrl",
        }

        self.assertIn("objecttype", data["_expand"])

    def test_patch_zaakobjecttype(self):
        self.client.force_login(self.user)

        changes = {"relatieOmschrijving": "Het is uit"}

        response = self.client.patch(self.endpoint, data=changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()

        expected = to_builtins(self.zaakobjecttype) | changes

        del data["_expand"]

        self.assertEqual(data, expected)

    def test_put_zaakobjecttype(self):
        self.client.force_login(self.user)
        objecttype = self.helper.create_objecttype()

        response = self.client.put(
            self.endpoint,
            data={
                "anderObjecttype": False,
                "objecttype": objecttype.url,
                "relatieOmschrijving": "In de PUT :(",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["zaaktype"], self.zaaktype.url)
        self.assertEqual(data["relatieOmschrijving"], "In de PUT :(")

    def test_delete_zaakobjecttype(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

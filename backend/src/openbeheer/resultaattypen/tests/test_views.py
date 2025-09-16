from msgspec import to_builtins
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.types.ztc import VertrouwelijkheidaanduidingEnum
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import VCRAPITestCase


class ResultaatTypeListViewTests(VCRAPITestCase):
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
        # create a fresh zaaktype and set its resultaattype endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        self.endpoint = reverse(
            "api:resultaattypen:resultaattypen-list",
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

    def test_retrieve_resultaattypen(self):
        # Frontend uses _expand instead, but this works too

        assert self.zaaktype.url
        resultaattype = self.helper.create_resultaattype(zaaktype=self.zaaktype.url)

        self.client.force_login(self.user)
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["pagination"]["count"], 1)
        created = to_builtins(resultaattype)
        self.assertEqual(data["results"][0], created)

    def test_create(self):
        "Create a new resultaattype for a zaaktype"
        self.client.force_login(self.user)
        response = self.client.post(
            self.endpoint,
            data={
                "omschrijving": "Vernieuwde receptuur",
                "resultaattypeomschrijving": "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/3a0a9c3c-0847-4e7e-b7d9-765b9434094c",
                "selectielijstklasse": "https://selectielijst.openzaak.nl/api/v1/resultaten/8af64c99-a168-40dd-8afd-9fbe0597b6dc",
                "archiefnominatie": "vernietigen",
                "brondatumArchiefprocedure": {
                    "afleidingswijze": "afgehandeld",
                    "procestermijn": None,
                    "datumkenmerk": "",
                    "einddatumBekend": False,
                    "objecttype": "",
                    "registratie": "",
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ResultaatTypeDetailViewTest(VCRAPITestCase):
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
        # create a fresh resultaattype and set its endpoint
        self.zaaktype = self.helper.create_zaaktype(
            vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar.value,
        )
        assert self.zaaktype.url
        self.resultaattype = self.helper.create_resultaattype(
            zaaktype=self.zaaktype.url
        )

        self.endpoint = reverse(
            "api:resultaattypen:resultaattypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
                "uuid": self.resultaattype.uuid,
            },
        )

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_resultaattype(self):
        self.client.force_login(self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        result_keys = set(data.keys())
        assert result_keys == {
            "zaaktype",
            "omschrijving",
            "resultaattypeomschrijving",
            "selectielijstklasse",
            "url",
            "zaaktypeIdentificatie",
            "omschrijvingGeneriek",
            "toelichting",
            "archiefnominatie",
            "archiefactietermijn",
            "brondatumArchiefprocedure",
            "procesobjectaard",
            "indicatieSpecifiek",
            "procestermijn",
            "catalogus",
            "besluittypen",
            "besluittypeOmschrijving",
            "informatieobjecttypen",
            "informatieobjecttypeOmschrijving",
            "beginGeldigheid",
            "eindeGeldigheid",
            "beginObject",
            "eindeObject",
        }

    def test_patch_resultaattype(self):
        self.client.force_login(self.user)

        changes = {"omschrijving": "MODIFIED by patch"}

        response = self.client.patch(self.endpoint, data=changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()

        expected = to_builtins(self.resultaattype) | changes

        del expected["uuid"]

        self.assertEqual(data, expected)

    def test_put_resultaattype(self):
        self.client.force_login(self.user)

        response = self.client.put(
            self.endpoint,
            data={
                "zaaktype": self.zaaktype.url,
                "omschrijving": "PUTjeschepper",
                "zaaktypeIdentificatie": "Something completely different",
                "resultaattypeomschrijving": "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/3a0a9c3c-0847-4e7e-b7d9-765b9434094c",
                "selectielijstklasse": "https://selectielijst.openzaak.nl/api/v1/resultaten/8af64c99-a168-40dd-8afd-9fbe0597b6dc",
                "archiefnominatie": "vernietigen",
                "brondatumArchiefprocedure": {
                    "afleidingswijze": "afgehandeld",
                    "procestermijn": None,
                    "datumkenmerk": "",
                    "einddatumBekend": False,
                    "objecttype": "",
                    "registratie": "",
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["zaaktype"], self.zaaktype.url)
        self.assertEqual(data["omschrijving"], "PUTjeschepper")
        # this seems read only? But it doesn't return an error when we PUT it.
        self.assertNotEqual(
            data["zaaktypeIdentificatie"], "Something completely different"
        )
        self.assertEqual(
            data["zaaktypeIdentificatie"], self.resultaattype.zaaktype_identificatie
        )
        self.assertEqual(
            data["resultaattypeomschrijving"],
            "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/3a0a9c3c-0847-4e7e-b7d9-765b9434094c",
        )
        self.assertEqual(
            data["selectielijstklasse"],
            "https://selectielijst.openzaak.nl/api/v1/resultaten/8af64c99-a168-40dd-8afd-9fbe0597b6dc",
        )
        self.assertEqual(data["archiefnominatie"], "vernietigen")
        self.assertEqual(
            data["brondatumArchiefprocedure"],
            {
                "afleidingswijze": "afgehandeld",
                "procestermijn": None,
                "datumkenmerk": "",
                "einddatumBekend": False,
                "objecttype": "",
                "registratie": "",
            },
        )

    def test_delete_resultaattype(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

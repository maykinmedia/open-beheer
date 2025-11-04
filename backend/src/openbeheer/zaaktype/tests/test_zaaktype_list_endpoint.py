from msgspec import convert, to_builtins
from requests import get
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.types._open_beheer import EigenschapWithUUID, ResultaatTypeWithUUID
from openbeheer.types.ztc import Status
from openbeheer.utils.open_zaak_helper.data_creation import (
    OpenZaakDataCreationHelper,
)
from openbeheer.utils.tests import VCRAPITestCase


class ZaakTypeListViewTest(VCRAPITestCase):
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
        cls.url = reverse("api:zaaktypen:zaaktype-list", kwargs={"slug": "OZ"})

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        data = response.json()

        self.assertGreater(data["pagination"]["count"], 0)

        field_names = [f["name"] for f in data["fields"]]

        # has specced fields in correct order
        self.assertListEqual(
            field_names,
            [
                "url",
                "identificatie",
                "omschrijving",
                "vertrouwelijkheidaanduiding",
                "versiedatum",
                "actief",
                "eindeGeldigheid",
                "concept",
            ],
        )

        # all rows have at least all fields
        for row in data["results"]:
            keys_in_fields = set(row.keys()) & set(field_names)
            self.assertSetEqual(keys_in_fields, set(field_names))

        identificatie = data["fields"][1]
        assert identificatie["name"] == "identificatie"
        # options should be undefined if there are no options
        # [] renders to an empty select
        self.assertNotIn("options", identificatie.keys())

        # no editable fields
        assert {repr(f) for f in data["fields"] if f.get("editable")} == set()

        versiedatum = next(f for f in data["fields"] if f["name"] == "versiedatum")
        self.assertEqual(versiedatum["type"], "date")

    def test_catalog_filter(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            self.url, query_params={"catalogus": "ec77ad39-0954-4aeb-bcf2-1beefbadf00d"}
        )

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["pagination"]["count"], 0)
        self.assertEqual(data["results"], [])

        response = self.client.get(
            self.url, query_params={"catalogus": "ec77ad39-0954-4aeb-bcf2-6f45263cde77"}
        )

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(data["pagination"]["count"], 0)
        self.assertGreater(len(data["results"]), 0)

    def test_datum_geldigheid_filter(self):
        self.client.force_authenticate(self.user)
        url = reverse("api:zaaktypen:zaaktype-list", kwargs={"slug": "OZ"})

        response = self.client.get(url, query_params={"datumGeldigheid": "2001-01-01"})

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["pagination"]["count"], 0)
        self.assertEqual(data["results"], [])

    def test_page_request(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url, query_params={"page": 1})

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(data["pagination"]["count"], 0)
        self.assertGreater(len(data["results"]), 0)

        self.assertEqual(data["pagination"]["page"], 1)

    def test_status_filter(self):
        self.client.force_authenticate(self.user)

        for status_param in Status:
            with self.subTest(f"{status_param=}"):
                response = self.client.get(
                    self.url, query_params={"status": status_param.value}
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_identificatie_filter(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            self.url, query_params={"identificatie": "ZAAKTYPE-2018-0000000001"}
        )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(data["pagination"]["count"], 0)
        self.assertGreater(len(data["results"]), 0)

        self.assertSetEqual(
            {r["identificatie"] for r in data["results"]}, {"ZAAKTYPE-2018-0000000001"}
        )

    def test_identificatie_partial_filter(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            self.url, query_params={"identificatie__icontains": "type-2018-0000000002"}
        )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(data["pagination"]["count"], 0)
        self.assertGreater(len(data["results"]), 0)

        self.assertSetEqual(
            {r["identificatie"] for r in data["results"]}, {"ZAAKTYPE-2018-0000000002"}
        )

    def test_omschrijving_partial_filter(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            self.url, query_params={"omschrijving__icontains": "destruction"}
        )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(data["pagination"]["count"], 0)
        self.assertGreater(len(data["results"]), 0)

        self.assertTrue(
            all("destruction" in r["omschrijving"].lower() for r in data["results"])
        )

    def test_trefwoorden_filter_single_word(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url, query_params={"trefwoorden": "foo"})

        response.json()  # TODO: Add some to the fixtures?

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_trefwoorden_filter_multi_word(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url, query_params={"trefwoorden": "foo,bar"})

        response.json()  # TODO: Add some to the fixtures?

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ZaakTypeCreateViewTest(VCRAPITestCase):
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
        cls.helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")
        cls.user = UserFactory.create()
        cls.url = reverse("api:zaaktypen:zaaktype-list", kwargs={"slug": "OZ"})

    def test_create_zaaktype(self):
        self.client.force_login(self.user)

        data = {
            "omschrijving": "New Zaaktype 001",
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
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn("uuid", response.json())

    def test_create_zaaktype_with_related_resultaattype(self):
        self.client.force_login(self.user)

        template_resultaattype = self.helper.create_resultaattype()
        selectielijstklasse = get(template_resultaattype.selectielijstklasse).json()
        resultaattype = to_builtins(template_resultaattype)
        del resultaattype["zaaktype"]
        del resultaattype["uuid"]
        resultaattype["catalogus"] = (
            "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77"
        )

        data = {
            "omschrijving": "New Zaaktype 001",
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
            # needs to be the same as resultaattype
            "selectielijstProcestype": selectielijstklasse["procesType"],
            "verantwoordelijke": "200000000",
            "beginGeldigheid": "2025-06-19",
            "versiedatum": "2025-06-19",
            "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
            "besluittypen": [],
            "gerelateerdeZaaktypen": [],
            "resultaattypen": [],
            "_expand": {"resultaattypen": [resultaattype]},
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_zaaktype = response.json()

        self.assertEqual(len(created_zaaktype["resultaattypen"]), 1)

        created_resultaattype_url = created_zaaktype["resultaattypen"][0]
        self.assertNotEqual(created_resultaattype_url, resultaattype["url"])

        expected_resultaattype = to_builtins(
            convert(
                resultaattype
                | {
                    "zaaktype": created_zaaktype["url"],
                    "zaaktypeIdentificatie": created_zaaktype["identificatie"],
                    "url": created_resultaattype_url,
                },
                ResultaatTypeWithUUID,
            )
        )
        assert (
            created_zaaktype["_expand"]["resultaattypen"][0] == expected_resultaattype
        )

    def test_create_zaaktype_with_multiple_related_besluitttype(self):
        self.client.force_login(self.user)

        data = {
            "omschrijving": "New Zaaktype 001",
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
            "resultaattypen": [],
            "_expand": {
                "besluittypen": [
                    {
                        "publicatieIndicatie": False,
                        "informatieobjecttypen": [],
                        "beginGeldigheid": "2025-06-19",
                        "catalogus": (
                            "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77"
                        ),
                    },
                    {
                        "publicatieIndicatie": True,
                        "informatieobjecttypen": [],
                        "beginGeldigheid": "2025-06-19",
                        "catalogus": (
                            "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77"
                        ),
                    },
                ]
            },
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_zaaktype = response.json()

        self.assertEqual(len(created_zaaktype["besluittypen"]), 2)

        self.assertSetEqual(
            set(created_zaaktype["besluittypen"]),
            {et["url"] for et in created_zaaktype["_expand"]["besluittypen"]},
        )

    def test_create_zaaktype_with_new_and_existing_besluitttypen(self):
        self.client.force_login(self.user)

        existing = self.helper.create_besluittype(
            catalogus="http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
        )

        data = {
            "omschrijving": "New Zaaktype 001",
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
            "besluittypen": [existing.url],
            "gerelateerdeZaaktypen": [],
            "resultaattypen": [],
            "_expand": {
                "besluittypen": [
                    {
                        "publicatieIndicatie": False,
                        "informatieobjecttypen": [],
                        "beginGeldigheid": "2025-06-19",
                        "catalogus": (
                            "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77"
                        ),
                    },
                    {
                        "publicatieIndicatie": True,
                        "informatieobjecttypen": [],
                        "beginGeldigheid": "2025-06-19",
                        "catalogus": (
                            "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77"
                        ),
                    },
                ]
            },
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_zaaktype = response.json()

        self.assertEqual(len(created_zaaktype["besluittypen"]), 3)

        self.assertSetEqual(
            set(created_zaaktype["besluittypen"]),
            {et["url"] for et in created_zaaktype["_expand"]["besluittypen"]}
            | {existing.url},
        )

    def test_create_zaaktype_with_related_statustype(self):
        self.client.force_login(self.user)

        data = {
            "omschrijving": "New Zaaktype 001",
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
            "resultaattypen": [],
            "_expand": {
                "statustypen": [
                    {
                        "omschrijving": "Status",
                        "volgnummer": 1,
                    },
                ]
            },
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_zaaktype = response.json()

        self.assertEqual(len(created_zaaktype["statustypen"]), 1)
        self.assertSetEqual(
            set(created_zaaktype["statustypen"]),
            {et["url"] for et in created_zaaktype["_expand"]["statustypen"]},
        )

    def test_create_zaaktype_with_related_eigenschappen(self):
        self.client.force_login(self.user)

        data = {
            "omschrijving": "New Zaaktype 001",
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
            "resultaattypen": [],
            "_expand": {
                "eigenschappen": [
                    {
                        "naam": "Eigenschap",
                        "definitie": "zelfst.naamw. (v.) iets wat karakteristiek is voor iemand of iets",
                        "specificatie": {
                            "formaat": "tekst",
                            "lengte": "255",
                            "kardinaliteit": "N",
                        },
                    },
                ]
            },
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_zaaktype = response.json()

        self.assertEqual(len(created_zaaktype["eigenschappen"]), 1)
        self.assertSetEqual(
            set(created_zaaktype["eigenschappen"]),
            {et["url"] for et in created_zaaktype["_expand"]["eigenschappen"]},
        )

        expanded_eigenschap = created_zaaktype["_expand"]["eigenschappen"][0]

        # should EigenschapWithUUID according to our OAS
        expected_eigenschap = to_builtins(
            convert(expanded_eigenschap, EigenschapWithUUID)
        )

        self.assertEqual(expanded_eigenschap, expected_eigenschap)

    def test_create_zaaktype_with_related_informatieobjecttypen(self):
        self.client.force_login(self.user)

        data = {
            "omschrijving": "New Zaaktype 001",
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
            "resultaattypen": [],
            "_expand": {
                "informatieobjecttypen": [
                    {
                        "omschrijving": "Gewoon een bestand",
                        "vertrouwelijkheidaanduiding": "geheim",
                        "informatieobjectcategorie": "Aard- en nagelvast",
                        "beginGeldigheid": "2025-07-30",
                    },
                ]
            },
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_zaaktype = response.json()

        self.assertEqual(len(created_zaaktype["informatieobjecttypen"]), 1)
        self.assertSetEqual(
            set(created_zaaktype["informatieobjecttypen"]),
            {et["url"] for et in created_zaaktype["_expand"]["informatieobjecttypen"]},
        )

    def test_create_zaaktype_with_related_roltypen(self):
        self.client.force_login(self.user)

        data = {
            "omschrijving": "New Zaaktype 001",
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
            "resultaattypen": [],
            "_expand": {
                "roltypen": [
                    {
                        "omschrijving": "Fruitella",
                        "omschrijvingGeneriek": "behandelaar",
                        "beginGeldigheid": "2025-07-30",
                    },
                    {
                        "omschrijving": "Droptella",
                        "omschrijvingGeneriek": "beslisser",
                        "beginGeldigheid": "2025-07-30",
                    },
                ]
            },
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_zaaktype = response.json()

        self.assertEqual(len(created_zaaktype["roltypen"]), 2)
        self.assertSetEqual(
            set(created_zaaktype["roltypen"]),
            {et["url"] for et in created_zaaktype["_expand"]["roltypen"]},
        )

    def test_create_zaaktype_with_existing_deelzaaktypen(self):
        self.client.force_login(self.user)

        existing = self.helper.create_zaaktype(
            omschrijving="Sub Zaaktype 000",
            catalogus="http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
        )
        data = {
            "omschrijving": "New Zaaktype 001",
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
            "resultaattypen": [],
            "deelzaaktypen": [existing.url],
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_zaaktype = response.json()

        self.assertEqual(len(created_zaaktype["deelzaaktypen"]), 1)
        self.assertSetEqual(
            set(created_zaaktype["deelzaaktypen"]),
            {existing.url},
        )

    def test_create_zaaktype_with_zaakobjecttypen(self):
        self.client.force_login(self.user)
        data = {
            "omschrijving": "New Zaaktype 001",
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
            "resultaattypen": [],
            "_expand": {
                "zaakobjecttypen": [
                    {
                        "anderObjecttype": False,
                        "objecttype": "https://www.gemeentelijkgegevensmodel.nl/latest/definities/definitie_Model%20Kern%20RSGB",
                        "relatieOmschrijving": "puzzle",
                    },
                ]
            },
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_zaaktype = response.json()

        self.assertEqual(len(created_zaaktype["zaakobjecttypen"]), 1)
        self.assertSetEqual(
            set(created_zaaktype["zaakobjecttypen"]),
            {et["url"] for et in created_zaaktype["_expand"]["zaakobjecttypen"]},
        )

    def test_missing_data(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            data={
                # "omschrijving": "New Zaaktype 001", # Missing!
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
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["invalidParams"][0]["name"], "omschrijving")
        self.assertEqual(response.json()["invalidParams"][0]["code"], "required")

    def test_create_zaaktype_with_related_resource_with_incomplete_data(self):
        self.client.force_login(self.user)
        catalogus = self.helper.create_catalogus()

        data = {
            "omschrijving": "New Zaaktype 001",
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
            "catalogus": catalogus.url,
            "besluittypen": [],
            "gerelateerdeZaaktypen": [],
            "resultaattypen": [],
            "_expand": {
                "roltypen": [
                    {
                        # "omschrijving": "Fruitella", # Missing!
                        "omschrijvingGeneriek": "behandelaar",
                        "beginGeldigheid": "2025-07-30",
                    },
                    {
                        "omschrijving": "Droptella",
                        "omschrijvingGeneriek": "beslisser",
                        "beginGeldigheid": "2025-07-30",
                    },
                ]
            },
        }
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.json()

        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[0]["invalidParams"][0]["name"], "roltypen.0.omschrijving"
        )

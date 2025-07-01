from django.test import tag
from faker import Faker
from furl import furl
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from maykin_common.vcr import VCRMixin
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory
from msgspec.json import decode

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.clients import ztc_client
from openbeheer.types.ztc import ZaakType


@tag("vcr")
class ZaakTypeDetailViewTest(VCRMixin, APITestCase):
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

    def _create_zaaktype(self) -> ZaakType:
        faker = Faker()

        with ztc_client("OZ") as client:
            response = client.post(
                "zaaktypen",
                json={
                    "omschrijving": faker.sentence(),
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
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        return decode(
            response.content,
            type=ZaakType,
            strict=False,
        )

    def test_not_authenticated(self):
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.cassette.play_count, 0)

    def test_retrieve_zaaktype(self):
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )

        self.client.force_login(self.user)
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)
        self.assertIn("fields", data)

        fields = {f["name"] for f in data["fields"]}
        # misspelled too, to catch camelize bugs
        expand = {"_expand", "Expand"}
        # fields are still undefined for expansion
        self.assertSetEqual(fields & expand, set())
        # all fields should exist on the result
        self.assertSetEqual(fields, set(data["result"].keys()) - {"_expand"})

        self.assertEqual(len(data["versions"]), 8)

        zaaktype = data["result"]

        with self.subTest("result"):
            self.assertEqual(zaaktype["omschrijving"], "Testing resultaattypen process")
            self.assertEqual(zaaktype["vertrouwelijkheidaanduiding"], "openbaar")
            self.assertEqual(
                zaaktype["doel"],
                "Trouble red compare produce animal. Everything today Democrat student enter. By probably adult.",
            )
            self.assertEqual(
                zaaktype["aanleiding"],
                "Couple toward trip old nice memory system instead.",
            )
            self.assertEqual(zaaktype["indicatieInternOfExtern"], "extern")
            self.assertEqual(zaaktype["handelingInitiator"], "indienen")
            self.assertEqual(zaaktype["onderwerp"], "Evenementvergunning")
            self.assertEqual(zaaktype["handelingBehandelaar"], "uitvoeren")
            self.assertEqual(zaaktype["doorlooptijd"], "P30D")
            self.assertTrue(zaaktype["opschortingEnAanhoudingMogelijk"])
            self.assertFalse(zaaktype["verlengingMogelijk"])
            self.assertTrue(zaaktype["publicatieIndicatie"])
            self.assertEqual(
                zaaktype["productenOfDiensten"], ["https://example.com/product/123"]
            )
            self.assertEqual(
                zaaktype["referentieproces"], {"naam": "ReferentieProces 0", "link": ""}
            )
            self.assertEqual(zaaktype["verantwoordelijke"], "100000000")
            self.assertEqual(zaaktype["beginGeldigheid"], "2018-01-01")
            self.assertEqual(zaaktype["versiedatum"], "2018-01-01")
            self.assertEqual(
                zaaktype["catalogus"],
                "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
            )
            self.assertEqual(zaaktype["besluittypen"], [])
            self.assertEqual(zaaktype["gerelateerdeZaaktypen"], [])
            self.assertEqual(
                zaaktype["url"],
                "http://localhost:8003/catalogi/api/v1/zaaktypen/ec9ebcdb-b652-466d-a651-fdb8ea787487",
            )
            self.assertEqual(zaaktype["identificatie"], "ZAAKTYPE-2020-0000000001")
            self.assertEqual(zaaktype["omschrijvingGeneriek"], "")
            self.assertEqual(zaaktype["toelichting"], "")
            self.assertIsNone(zaaktype["servicenorm"])
            self.assertIsNone(zaaktype["verlengingstermijn"])
            self.assertEqual(zaaktype["trefwoorden"], [])
            self.assertEqual(zaaktype["publicatietekst"], "")
            self.assertEqual(zaaktype["verantwoordingsrelatie"], [])
            self.assertEqual(
                zaaktype["selectielijstProcestype"],
                "https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0",
            )
            self.assertFalse(zaaktype["concept"])
            self.assertIsNone(zaaktype["broncatalogus"])
            self.assertIsNone(zaaktype["bronzaaktype"])
            self.assertIsNone(zaaktype["eindeGeldigheid"])
            self.assertEqual(zaaktype["beginObject"], "2018-01-01")
            self.assertIsNone(zaaktype["eindeObject"])
            self.assertEqual(zaaktype["statustypen"], [])
            self.assertEqual(
                zaaktype["resultaattypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/resultaattypen/b9109699-67cd-4c2e-a2cf-76b311d40e25",
                    "http://localhost:8003/catalogi/api/v1/resultaattypen/7759dcb7-de9a-4543-99e3-81472c488f32",
                ],
            )
            self.assertEqual(zaaktype["eigenschappen"], [])
            self.assertEqual(zaaktype["informatieobjecttypen"], [])
            self.assertEqual(
                zaaktype["roltypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/roltypen/ae39e60c-0e4b-4432-a830-8755ed083fda"
                ],
            )
            self.assertEqual(zaaktype["deelzaaktypen"], [])
            self.assertEqual(zaaktype["zaakobjecttypen"], [])

            self.assertEqual(
                zaaktype["_expand"],
                {
                    "besluittypen": [],
                    "eigenschappen": [],
                    "informatieobjecttypen": [],
                    "resultaattypen": [
                        {
                            "archiefactietermijn": None,
                            "archiefnominatie": "",
                            "beginGeldigheid": None,
                            "beginObject": None,
                            "besluittypeOmschrijving": [],
                            "besluittypen": [],
                            "brondatumArchiefprocedure": {
                                "afleidingswijze": "",
                                "datumkenmerk": "",
                                "einddatumBekend": False,
                                "objecttype": "",
                                "procestermijn": None,
                                "registratie": "",
                            },
                            "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
                            "eindeGeldigheid": None,
                            "eindeObject": None,
                            "indicatieSpecifiek": None,
                            "informatieobjecttypeOmschrijving": [],
                            "informatieobjecttypen": [],
                            "omschrijving": "Lopend",
                            "omschrijvingGeneriek": "",
                            "procesobjectaard": "",
                            "procestermijn": None,
                            "resultaattypeomschrijving": "Lopend",
                            "selectielijstklasse": "https://selectielijst.openzaak.nl/api/v1/resultaten/cc5ae4e3-a9e6-4386-bcee-46be4986a829",
                            "toelichting": "",
                            "url": "http://localhost:8003/catalogi/api/v1/resultaattypen/7759dcb7-de9a-4543-99e3-81472c488f32",
                            "zaaktype": "http://localhost:8003/catalogi/api/v1/zaaktypen/ec9ebcdb-b652-466d-a651-fdb8ea787487",
                            "zaaktypeIdentificatie": "ZAAKTYPE-2020-0000000001",
                        },
                        {
                            "archiefactietermijn": None,
                            "archiefnominatie": "",
                            "beginGeldigheid": None,
                            "beginObject": None,
                            "besluittypeOmschrijving": [],
                            "besluittypen": [],
                            "brondatumArchiefprocedure": {
                                "afleidingswijze": "",
                                "datumkenmerk": "",
                                "einddatumBekend": False,
                                "objecttype": "",
                                "procestermijn": None,
                                "registratie": "",
                            },
                            "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
                            "eindeGeldigheid": None,
                            "eindeObject": None,
                            "indicatieSpecifiek": None,
                            "informatieobjecttypeOmschrijving": [],
                            "informatieobjecttypen": [],
                            "omschrijving": "Afgehandeld",
                            "omschrijvingGeneriek": "",
                            "procesobjectaard": "",
                            "procestermijn": None,
                            "resultaattypeomschrijving": "Afgehandeld",
                            "selectielijstklasse": "https://selectielijst.openzaak.nl/api/v1/resultaten/1bb001e9-5eab-4f10-8940-8781e11f180f",
                            "toelichting": "",
                            "url": "http://localhost:8003/catalogi/api/v1/resultaattypen/b9109699-67cd-4c2e-a2cf-76b311d40e25",
                            "zaaktype": "http://localhost:8003/catalogi/api/v1/zaaktypen/ec9ebcdb-b652-466d-a651-fdb8ea787487",
                            "zaaktypeIdentificatie": "ZAAKTYPE-2020-0000000001",
                        },
                    ],
                    "roltypen": [
                        {
                            "beginGeldigheid": None,
                            "beginObject": None,
                            "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
                            "eindeGeldigheid": None,
                            "eindeObject": None,
                            "omschrijving": "Behandelend afdeling",
                            "omschrijvingGeneriek": "behandelaar",
                            "url": "http://localhost:8003/catalogi/api/v1/roltypen/ae39e60c-0e4b-4432-a830-8755ed083fda",
                            "zaaktype": "http://localhost:8003/catalogi/api/v1/zaaktypen/ec9ebcdb-b652-466d-a651-fdb8ea787487",
                            "zaaktypeIdentificatie": "ZAAKTYPE-2020-0000000001",
                        }
                    ],
                    "statustypen": [],
                    "deelzaaktypen": [],
                    "zaakobjecttypen": [],
                },
            )

        with self.subTest("fields"):
            self.assertEqual(data["fields"][1]["name"], "vertrouwelijkheidaanduiding")
            self.assertEqual(len(data["fields"][1]["options"]), 8)

    def test_patch_zaaktype(self):
        zaaktype = self._create_zaaktype()

        assert zaaktype.url
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]

        # Now modify the zaaktype
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": zaaktype_uuid},
        )
        self.client.force_login(self.user)

        response = self.client.patch(
            endpoint, data={"omschrijving": "MODIFIED by test test_patch_zaaktype"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)

        self.assertEqual(len(data["versions"]), 1)

        zaaktype = data["result"]

        with self.subTest("Modified field"):
            self.assertEqual(
                zaaktype["omschrijving"], "MODIFIED by test test_patch_zaaktype"
            )

        with self.subTest("Not modified fields"):
            self.assertTrue(zaaktype["concept"])
            self.assertEqual(zaaktype["vertrouwelijkheidaanduiding"], "geheim")
            self.assertEqual(
                zaaktype["doel"],
                "New Zaaktype 001",
            )
            self.assertEqual(
                zaaktype["aanleiding"],
                "New Zaaktype 001",
            )
            self.assertEqual(zaaktype["indicatieInternOfExtern"], "intern")
            self.assertEqual(zaaktype["handelingInitiator"], "aanvragen")
            self.assertEqual(zaaktype["onderwerp"], "New Zaaktype 001")
            self.assertEqual(zaaktype["handelingBehandelaar"], "handelin")
            self.assertEqual(zaaktype["doorlooptijd"], "P40D")
            self.assertFalse(zaaktype["opschortingEnAanhoudingMogelijk"])
            self.assertTrue(zaaktype["verlengingMogelijk"])
            self.assertFalse(zaaktype["publicatieIndicatie"])
            self.assertEqual(
                zaaktype["productenOfDiensten"], ["https://example.com/product/321"]
            )
            self.assertEqual(
                zaaktype["referentieproces"], {"naam": "ReferentieProces 1", "link": ""}
            )
            self.assertEqual(zaaktype["verantwoordelijke"], "200000000")
            self.assertEqual(zaaktype["beginGeldigheid"], "2025-06-19")
            self.assertEqual(zaaktype["versiedatum"], "2025-06-19")
            self.assertEqual(
                zaaktype["catalogus"],
                "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
            )
            self.assertEqual(zaaktype["besluittypen"], [])
            self.assertEqual(zaaktype["gerelateerdeZaaktypen"], [])

    def test_put_zaaktype(self):
        zaaktype = self._create_zaaktype()

        assert zaaktype.url
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]

        # Now modify the zaaktype
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": zaaktype_uuid},
        )
        self.client.force_login(self.user)

        response = self.client.put(
            endpoint,
            data={
                "omschrijving": "MODIFIED by test test_put_zaaktype",
                "vertrouwelijkheidaanduiding": "openbaar",
                "doel": "MODIFIED",
                "aanleiding": "MODIFIED",
                "indicatieInternOfExtern": "extern",
                "handelingInitiator": "indienen",
                "onderwerp": "MODIFIED",
                "handelingBehandelaar": "handelin",
                "doorlooptijd": "P30D",
                "opschortingEnAanhoudingMogelijk": False,
                "verlengingMogelijk": False,
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)

        self.assertEqual(len(data["versions"]), 1)

        zaaktype = data["result"]

        # Now check the modified values
        self.assertEqual(zaaktype["omschrijving"], "MODIFIED by test test_put_zaaktype")
        self.assertTrue(zaaktype["concept"])
        self.assertEqual(zaaktype["vertrouwelijkheidaanduiding"], "openbaar")
        self.assertEqual(
            zaaktype["doel"],
            "MODIFIED",
        )
        self.assertEqual(
            zaaktype["aanleiding"],
            "MODIFIED",
        )
        self.assertEqual(zaaktype["indicatieInternOfExtern"], "extern")
        self.assertEqual(zaaktype["handelingInitiator"], "indienen")
        self.assertEqual(zaaktype["onderwerp"], "MODIFIED")
        self.assertEqual(zaaktype["handelingBehandelaar"], "handelin")
        self.assertEqual(zaaktype["doorlooptijd"], "P30D")
        self.assertFalse(zaaktype["opschortingEnAanhoudingMogelijk"])
        self.assertFalse(zaaktype["verlengingMogelijk"])
        self.assertFalse(zaaktype["publicatieIndicatie"])
        self.assertEqual(
            zaaktype["productenOfDiensten"], ["https://example.com/product/321"]
        )
        self.assertEqual(
            zaaktype["referentieproces"], {"naam": "ReferentieProces 1", "link": ""}
        )
        self.assertEqual(zaaktype["verantwoordelijke"], "200000000")
        self.assertEqual(zaaktype["beginGeldigheid"], "2025-06-19")
        self.assertEqual(zaaktype["versiedatum"], "2025-06-19")
        self.assertEqual(
            zaaktype["catalogus"],
            "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
        )
        self.assertEqual(zaaktype["besluittypen"], [])
        self.assertEqual(zaaktype["gerelateerdeZaaktypen"], [])
        self.assertEqual(zaaktype["omschrijvingGeneriek"], "")
        self.assertEqual(zaaktype["toelichting"], "")
        self.assertIsNone(zaaktype["servicenorm"])
        self.assertIsNone(
            zaaktype["verlengingstermijn"]
        )  # because verlengingMogelijk is false
        self.assertEqual(zaaktype["trefwoorden"], [])
        self.assertEqual(zaaktype["publicatietekst"], "")
        self.assertEqual(zaaktype["verantwoordingsrelatie"], [])
        self.assertIsNone(zaaktype["broncatalogus"])
        self.assertIsNone(zaaktype["bronzaaktype"])
        self.assertIsNone(zaaktype["eindeGeldigheid"])
        self.assertIsNone(zaaktype["eindeObject"])

    def test_proxy_error_response(self):
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )
        self.client.force_login(self.user)

        response = self.client.put(
            endpoint,
            data={
                "omschrijving": "MODIFIED",
                # Missing all the other required fields.
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()

        self.assertEqual(data["code"], "invalid")
        self.assertEqual(data["title"], "Invalid input.")

        invalid_params = {item["name"]: item["code"] for item in data["invalidParams"]}

        expected_required_fields = [
            "vertrouwelijkheidaanduiding",
            "doel",
            "aanleiding",
            "indicatieInternOfExtern",
            "handelingInitiator",
            "onderwerp",
            "handelingBehandelaar",
            "doorlooptijd",
            "opschortingEnAanhoudingMogelijk",
            "verlengingMogelijk",
            "publicatieIndicatie",
            "productenOfDiensten",
            "referentieproces",
            "verantwoordelijke",
            "beginGeldigheid",
            "versiedatum",
            "catalogus",
            "besluittypen",
            "gerelateerdeZaaktypen",
        ]

        for field in expected_required_fields:
            self.assertIn(field, invalid_params)
            self.assertEqual(invalid_params[field], "required")

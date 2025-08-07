from django.test import tag

from furl import furl
from maykin_common.vcr import VCRMixin
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper


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

        cls.helper = OpenZaakDataCreationHelper(service_identifier="OZ")

    def test_not_authenticated(self):
        endpoint = reverse(
            "api:zaaktypen:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.cassette.play_count, 0)

    def test_retrieve_zaaktype(self):
        zaaktype = self.helper.create_zaaktype(
            overrides={
                "selectielijstProcestype": "https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0"
            }
        )
        self.helper.create_resultaattype(
            overrides={
                "zaaktype": zaaktype.url,
                "omschrijving": "Toegekend",
                "resultaattypeomschrijving": "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/fb65d251-1518-4185-865f-b8bdcfad07b1",
                "selectielijstklasse": "https://selectielijst.openzaak.nl/api/v1/resultaten/afa30940-855b-4a7e-aa21-9e15a8078814",
            }
        )
        self.helper.create_resultaattype(
            overrides={
                "zaaktype": zaaktype.url,
                "omschrijving": "Afgehandeld",
                "resultaattypeomschrijving": "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/7cb315fb-4f7b-4a43-aca1-e4522e4c73b3",
                "selectielijstklasse": "https://selectielijst.openzaak.nl/api/v1/resultaten/8af64c99-a168-40dd-8afd-9fbe0597b6dc",
            }
        )
        self.helper.create_roltype(
            overrides={
                "zaaktype": zaaktype.url,
                "omschrijving": "Behandelend afdeling",
                "omschrijvingGeneriek": "behandelaar",
            }
        )

        assert zaaktype.url
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]
        self.client.force_login(self.user)

        endpoint = reverse(
            "api:zaaktypen:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": zaaktype_uuid},
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)
        self.assertIn("fields", data)

        fields_by_name = {f["name"]: f for f in data["fields"]}
        fields = set(fields_by_name)
        # misspelled too, to catch camelize bugs
        expand = {"_expand", "Expand"}
        # fields are still undefined for expansion
        self.assertSetEqual(fields & expand, set())
        # all fields should exist on the result
        self.assertSetEqual(fields, set(data["result"].keys()) - {"_expand"})

        self.assertEqual(len(data["versions"]), 1)

        zaaktype = data["result"]

        with self.subTest("result"):
            self.assertIn("omschrijving", zaaktype)
            self.assertIn("vertrouwelijkheidaanduiding", zaaktype)
            self.assertIn("doel", zaaktype)
            self.assertIn("aanleiding", zaaktype)
            self.assertIn("indicatieInternOfExtern", zaaktype)
            self.assertIn("handelingInitiator", zaaktype)
            self.assertIn("onderwerp", zaaktype)
            self.assertIn("handelingBehandelaar", zaaktype)
            self.assertIn("doorlooptijd", zaaktype)
            self.assertIn("opschortingEnAanhoudingMogelijk", zaaktype)
            self.assertIn("verlengingMogelijk", zaaktype)
            self.assertIn("publicatieIndicatie", zaaktype)
            self.assertIn("productenOfDiensten", zaaktype)
            self.assertIn("referentieproces", zaaktype)
            self.assertIn("verantwoordelijke", zaaktype)
            self.assertIn("beginGeldigheid", zaaktype)
            self.assertIn("versiedatum", zaaktype)
            self.assertIn("catalogus", zaaktype)
            self.assertIn("besluittypen", zaaktype)
            self.assertIn("gerelateerdeZaaktypen", zaaktype)
            self.assertIn("url", zaaktype)
            self.assertIn("identificatie", zaaktype)
            self.assertIn("omschrijvingGeneriek", zaaktype)
            self.assertIn("toelichting", zaaktype)
            self.assertIn("servicenorm", zaaktype)
            self.assertIn("verlengingstermijn", zaaktype)
            self.assertIn("trefwoorden", zaaktype)
            self.assertIn("publicatietekst", zaaktype)
            self.assertIn("verantwoordingsrelatie", zaaktype)
            self.assertIn("selectielijstProcestype", zaaktype)
            self.assertIn("concept", zaaktype)
            self.assertIn("broncatalogus", zaaktype)
            self.assertIn("bronzaaktype", zaaktype)
            self.assertIn("eindeGeldigheid", zaaktype)
            self.assertIn("beginObject", zaaktype)
            self.assertIn("eindeObject", zaaktype)
            self.assertIn("statustypen", zaaktype)
            self.assertIn("resultaattypen", zaaktype)
            self.assertIn("eigenschappen", zaaktype)
            self.assertIn("informatieobjecttypen", zaaktype)
            self.assertIn("roltypen", zaaktype)
            self.assertIn("deelzaaktypen", zaaktype)
            self.assertIn("zaakobjecttypen", zaaktype)

            self.assertEqual(
                zaaktype["_expand"],
                {
                    "besluittypen": [],
                    "eigenschappen": [],
                    "informatieobjecttypen": [],
                    "resultaattypen": [
                        {
                            "url": "http://localhost:8003/catalogi/api/v1/resultaattypen/93eae5ed-ed79-4cc9-ac3f-6cca22dee395",
                            "zaaktype": "http://localhost:8003/catalogi/api/v1/zaaktypen/df34e352-ecc7-46cd-a18c-7998fac92716",
                            "zaaktypeIdentificatie": "ZAAKTYPE-2025-0000000058",
                            "omschrijving": "Afgehandeld",
                            "resultaattypeomschrijving": "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/7cb315fb-4f7b-4a43-aca1-e4522e4c73b3",
                            "omschrijvingGeneriek": "Afgehandeld",
                            "selectielijstklasse": "https://selectielijst.openzaak.nl/api/v1/resultaten/8af64c99-a168-40dd-8afd-9fbe0597b6dc",
                            "toelichting": "",
                            "archiefnominatie": "vernietigen",
                            "archiefactietermijn": None,
                            "brondatumArchiefprocedure": {
                                "afleidingswijze": "afgehandeld",
                                "datumkenmerk": "",
                                "einddatumBekend": False,
                                "objecttype": "",
                                "registratie": "",
                                "procestermijn": None,
                            },
                            "procesobjectaard": "",
                            "indicatieSpecifiek": None,
                            "procestermijn": None,
                            "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/d001f879-496e-4844-8a64-fcdd0eab6b23",
                            "besluittypen": [],
                            "besluittypeOmschrijving": [],
                            "informatieobjecttypen": [],
                            "informatieobjecttypeOmschrijving": [],
                            "beginGeldigheid": None,
                            "eindeGeldigheid": None,
                            "beginObject": None,
                            "eindeObject": None,
                        },
                        {
                            "url": "http://localhost:8003/catalogi/api/v1/resultaattypen/6052ca60-5062-4887-b0c1-a6c2b4fdec45",
                            "zaaktype": "http://localhost:8003/catalogi/api/v1/zaaktypen/df34e352-ecc7-46cd-a18c-7998fac92716",
                            "zaaktypeIdentificatie": "ZAAKTYPE-2025-0000000058",
                            "omschrijving": "Toegekend",
                            "resultaattypeomschrijving": "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/fb65d251-1518-4185-865f-b8bdcfad07b1",
                            "omschrijvingGeneriek": "Toegekend",
                            "selectielijstklasse": "https://selectielijst.openzaak.nl/api/v1/resultaten/afa30940-855b-4a7e-aa21-9e15a8078814",
                            "toelichting": "",
                            "archiefnominatie": "vernietigen",
                            "archiefactietermijn": "P10Y",
                            "brondatumArchiefprocedure": {
                                "afleidingswijze": "afgehandeld",
                                "datumkenmerk": "",
                                "einddatumBekend": False,
                                "objecttype": "",
                                "registratie": "",
                                "procestermijn": None,
                            },
                            "procesobjectaard": "",
                            "indicatieSpecifiek": None,
                            "procestermijn": None,
                            "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/d001f879-496e-4844-8a64-fcdd0eab6b23",
                            "besluittypen": [],
                            "besluittypeOmschrijving": [],
                            "informatieobjecttypen": [],
                            "informatieobjecttypeOmschrijving": [],
                            "beginGeldigheid": None,
                            "eindeGeldigheid": None,
                            "beginObject": None,
                            "eindeObject": None,
                        },
                    ],
                    "roltypen": [
                        {
                            "url": "http://localhost:8003/catalogi/api/v1/roltypen/81f05a62-0a3e-410e-9cf4-84aef33e8e3e",
                            "zaaktype": "http://localhost:8003/catalogi/api/v1/zaaktypen/df34e352-ecc7-46cd-a18c-7998fac92716",
                            "zaaktypeIdentificatie": "ZAAKTYPE-2025-0000000058",
                            "omschrijving": "Behandelend afdeling",
                            "omschrijvingGeneriek": "behandelaar",
                            "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/d001f879-496e-4844-8a64-fcdd0eab6b23",
                            "beginGeldigheid": None,
                            "eindeGeldigheid": None,
                            "beginObject": None,
                            "eindeObject": None,
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
            self.assertEqual(fields_by_name["beginGeldigheid"]["type"], "date")

    def test_patch_zaaktype(self):
        zaaktype = self.helper.create_zaaktype()

        assert zaaktype.url
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]

        # Now modify the zaaktype
        endpoint = reverse(
            "api:zaaktypen:zaaktype-detail",
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
            self.assertEqual(zaaktype["besluittypen"], [])
            self.assertEqual(zaaktype["gerelateerdeZaaktypen"], [])

    def test_put_zaaktype(self):
        zaaktype = self.helper.create_zaaktype()

        assert zaaktype.url
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]

        # Now modify the zaaktype
        endpoint = reverse(
            "api:zaaktypen:zaaktype-detail",
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
        zaaktype = self.helper.create_zaaktype()

        assert zaaktype.url
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]

        self.client.force_login(self.user)
        endpoint = reverse(
            "api:zaaktypen:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": zaaktype_uuid},
        )

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

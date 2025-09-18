import re
from unittest import skip

from django.test import tag

from furl import furl
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.config.tests.factories import APIConfigFactory
from openbeheer.utils.open_zaak_helper.data_creation import (
    OpenZaakDataCreationHelper,
)
from openbeheer.utils.tests import VCRAPITestCase


class ZaakTypeDetailViewTest(VCRAPITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        APIConfigFactory.create()
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
            "api:zaaktypen:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_zaaktype(self):
        zaaktype = self.helper.create_zaaktype(
            selectielijstProcestype="https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0"
        )
        assert zaaktype.url
        resultaattype1 = self.helper.create_resultaattype(
            zaaktype=zaaktype.url,
            omschrijving="Toegekend",
            resultaattypeomschrijving="https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/fb65d251-1518-4185-865f-b8bdcfad07b1",
            selectielijstklasse="https://selectielijst.openzaak.nl/api/v1/resultaten/afa30940-855b-4a7e-aa21-9e15a8078814",
        )
        resultaattype2 = self.helper.create_resultaattype(
            zaaktype=zaaktype.url,
            omschrijving="Afgehandeld",
            resultaattypeomschrijving="https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/7cb315fb-4f7b-4a43-aca1-e4522e4c73b3",
            selectielijstklasse="https://selectielijst.openzaak.nl/api/v1/resultaten/8af64c99-a168-40dd-8afd-9fbe0597b6dc",
        )
        roltype = self.helper.create_roltype(
            zaaktype=zaaktype.url,
            omschrijving="Behandelend afdeling",
            omschrijvingGeneriek="behandelaar",
        )
        statustype = self.helper.create_statustype(
            zaaktype.url, omschrijving="Omschrijving A"
        )

        iot = self.helper.create_informatieobjecttype(catalogus=zaaktype.catalogus)
        assert (
            iot.url
            and resultaattype1.url
            and resultaattype2.url
            and roltype.url
            and statustype.url
        )
        self.helper.relate_zaaktype_informatieobjecttype(zaaktype.url, iot.url)

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
        fields = {f for f in fields_by_name if not f.startswith("_expand")}
        # all fields should exist on the result
        self.assertSetEqual(fields, set(data["result"].keys()) - {"_expand"})

        # all expansion_fields should exist on the expansion
        expansion_fields = {
            f.split(".")[1] for f in fields_by_name if f.startswith("_expand")
        }
        # FIXME: the result won't have zaakobjecttypen (and therefore no objecttype), unless the zaaktype is published
        # see: open-zaak/open-zaak#2178
        self.assertSetEqual(
            expansion_fields - {"objecttype"}, set(data["result"]["_expand"])
        )

        self.assertEqual(len(data["versions"]), 1)

        zaaktype_data = data["result"]

        with self.subTest("result"):
            self.assertIn("uuid", zaaktype_data)
            self.assertIn("omschrijving", zaaktype_data)
            self.assertIn("vertrouwelijkheidaanduiding", zaaktype_data)
            self.assertIn("doel", zaaktype_data)
            self.assertIn("aanleiding", zaaktype_data)
            self.assertIn("indicatieInternOfExtern", zaaktype_data)
            self.assertIn("handelingInitiator", zaaktype_data)
            self.assertIn("onderwerp", zaaktype_data)
            self.assertIn("handelingBehandelaar", zaaktype_data)
            self.assertIn("doorlooptijd", zaaktype_data)
            self.assertIn("opschortingEnAanhoudingMogelijk", zaaktype_data)
            self.assertIn("verlengingMogelijk", zaaktype_data)
            self.assertIn("publicatieIndicatie", zaaktype_data)
            self.assertIn("productenOfDiensten", zaaktype_data)
            self.assertIn("referentieproces", zaaktype_data)
            self.assertIn("verantwoordelijke", zaaktype_data)
            self.assertIn("beginGeldigheid", zaaktype_data)
            self.assertIn("versiedatum", zaaktype_data)
            self.assertIn("catalogus", zaaktype_data)
            self.assertIn("besluittypen", zaaktype_data)
            self.assertIn("gerelateerdeZaaktypen", zaaktype_data)
            self.assertIn("url", zaaktype_data)
            self.assertIn("identificatie", zaaktype_data)
            self.assertIn("omschrijvingGeneriek", zaaktype_data)
            self.assertIn("toelichting", zaaktype_data)
            self.assertIn("servicenorm", zaaktype_data)
            self.assertIn("verlengingstermijn", zaaktype_data)
            self.assertIn("trefwoorden", zaaktype_data)
            self.assertIn("publicatietekst", zaaktype_data)
            self.assertIn("verantwoordingsrelatie", zaaktype_data)
            self.assertIn("selectielijstProcestype", zaaktype_data)
            self.assertIn("concept", zaaktype_data)
            self.assertIn("broncatalogus", zaaktype_data)
            self.assertIn("bronzaaktype", zaaktype_data)
            self.assertIn("eindeGeldigheid", zaaktype_data)
            self.assertIn("beginObject", zaaktype_data)
            self.assertIn("eindeObject", zaaktype_data)
            self.assertIn("statustypen", zaaktype_data)
            self.assertIn("resultaattypen", zaaktype_data)
            self.assertIn("eigenschappen", zaaktype_data)
            self.assertIn("informatieobjecttypen", zaaktype_data)
            self.assertIn("roltypen", zaaktype_data)
            self.assertIn("deelzaaktypen", zaaktype_data)
            self.assertIn("zaakobjecttypen", zaaktype_data)

            self.assertEqual(zaaktype_data["_expand"]["besluittypen"], [])
            self.assertEqual(zaaktype_data["_expand"]["eigenschappen"], [])
            self.assertEqual(
                zaaktype_data["_expand"]["informatieobjecttypen"],
                [
                    {
                        "uuid": furl(iot.url).path.segments[-1],
                        "catalogus": zaaktype.catalogus,
                        "omschrijving": "Omschrijving A",
                        "vertrouwelijkheidaanduiding": "openbaar",
                        "beginGeldigheid": "2025-07-01",
                        "informatieobjectcategorie": "Blue",
                        "url": iot.url,
                        "eindeGeldigheid": None,
                        "concept": True,
                        "besluittypen": [],
                        "trefwoord": [],
                        "omschrijvingGeneriek": {
                            "informatieobjecttypeOmschrijvingGeneriek": "",
                            "definitieInformatieobjecttypeOmschrijvingGeneriek": "",
                            "herkomstInformatieobjecttypeOmschrijvingGeneriek": "",
                            "hierarchieInformatieobjecttypeOmschrijvingGeneriek": "",
                            "opmerkingInformatieobjecttypeOmschrijvingGeneriek": "",
                        },
                        "zaaktypen": [zaaktype.url],
                        "beginObject": "2025-07-01",
                        "eindeObject": None,
                    }
                ],
            )

            expected_resultaattypen = [
                {
                    "uuid": furl(resultaattype1.url).path.segments[-1],
                    "url": resultaattype1.url,
                    "zaaktype": zaaktype.url,
                    "zaaktypeIdentificatie": zaaktype.identificatie,
                    "omschrijving": resultaattype1.omschrijving,
                    "resultaattypeomschrijving": resultaattype1.resultaattypeomschrijving,
                    "omschrijvingGeneriek": resultaattype1.omschrijving_generiek,
                    "selectielijstklasse": resultaattype1.selectielijstklasse,
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
                    "catalogus": zaaktype.catalogus,
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
                    "uuid": furl(resultaattype2.url).path.segments[-1],
                    "url": resultaattype2.url,
                    "zaaktype": zaaktype.url,
                    "zaaktypeIdentificatie": zaaktype.identificatie,
                    "omschrijving": resultaattype2.omschrijving,
                    "resultaattypeomschrijving": resultaattype2.resultaattypeomschrijving,
                    "omschrijvingGeneriek": resultaattype2.omschrijving_generiek,
                    "selectielijstklasse": resultaattype2.selectielijstklasse,
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
                    "catalogus": zaaktype.catalogus,
                    "besluittypen": [],
                    "besluittypeOmschrijving": [],
                    "informatieobjecttypen": [],
                    "informatieobjecttypeOmschrijving": [],
                    "beginGeldigheid": None,
                    "eindeGeldigheid": None,
                    "beginObject": None,
                    "eindeObject": None,
                },
            ]
            self.assertEqual(
                sorted(
                    zaaktype_data["_expand"]["resultaattypen"],
                    key=lambda item: item["uuid"],
                ),
                sorted(
                    expected_resultaattypen,
                    key=lambda item: item["uuid"],
                ),
            )
            self.assertEqual(
                zaaktype_data["_expand"]["roltypen"],
                [
                    {
                        "uuid": furl(roltype.url).path.segments[-1],
                        "url": roltype.url,
                        "zaaktype": zaaktype.url,
                        "zaaktypeIdentificatie": zaaktype.identificatie,
                        "omschrijving": "Behandelend afdeling",
                        "omschrijvingGeneriek": "behandelaar",
                        "catalogus": zaaktype.catalogus,
                        "beginGeldigheid": None,
                        "eindeGeldigheid": None,
                        "beginObject": None,
                        "eindeObject": None,
                    }
                ],
            )
            self.assertEqual(
                zaaktype_data["_expand"]["statustypen"],
                [
                    {
                        "uuid": furl(statustype.url).path.segments[-1],
                        "omschrijving": "Omschrijving A",
                        "zaaktype": zaaktype.url,
                        "volgnummer": 1,
                        "url": statustype.url,
                        "omschrijvingGeneriek": "",
                        "statustekst": "",
                        "zaaktypeIdentificatie": zaaktype.identificatie,
                        "isEindstatus": True,
                        "informeren": False,
                        "doorlooptijd": None,
                        "toelichting": None,
                        "checklistitemStatustype": [],
                        "catalogus": zaaktype.catalogus,
                        "eigenschappen": [],
                        "zaakobjecttypen": [],
                        "beginGeldigheid": None,
                        "eindeGeldigheid": None,
                        "beginObject": None,
                        "eindeObject": None,
                    }
                ],
            )
            self.assertEqual(zaaktype_data["_expand"]["deelzaaktypen"], [])
            self.assertEqual(zaaktype_data["_expand"]["zaakobjecttypen"], [])
            self.assertEqual(
                zaaktype_data["_expand"]["selectielijstProcestype"],
                {
                    "url": "https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0",
                    "nummer": 1,
                    "jaar": 2020,
                    "naam": "Instellen en inrichten organisatie",
                    "omschrijving": "Instellen en inrichten organisatie",
                    "toelichting": "Dit procestype betreft het instellen van een nieuw organisatieonderdeel of een nieuwe orgaan waar het orgaan in deelneemt. Dit procestype betreft eveneens het inrichten van het eigen orgaan. Dit kan kleinschalig plaatsvinden bijvoorbeeld het wijzigen van de uitvoering van een wettelijke taak of grootschalig wanneer er een organisatiewijziging wordt doorgevoerd.",
                    "procesobject": "De vastgestelde organisatie inrichting",
                },
            )

        vertrouwelijkheidaanduiding_field = next(
            (
                field
                for field in data["fields"]
                if field["name"] == "vertrouwelijkheidaanduiding"
            ),
            None,
        )
        assert vertrouwelijkheidaanduiding_field
        with self.subTest("fields"):
            self.assertEqual(len(vertrouwelijkheidaanduiding_field["options"]), 8)
            self.assertEqual(fields_by_name["beginGeldigheid"]["type"], "date")

            # has some editable fields
            assert any(f.get("editable") for f in fields_by_name.values())

        with self.subTest("All fields in the fieldsets should exist"):
            fields_in_fieldsets = set(
                sum((fieldset["fields"] for _, fieldset in data["fieldsets"]), [])
            )
            field_names = set(fields_by_name.keys())
            assert fields_in_fieldsets - field_names == set()

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

    @tag("gh-128")
    @skip(
        "Needs open zaak issue https://github.com/open-zaak/open-zaak/issues/2140 to be fixed."
    )
    def test_broncatalogus_fields(self):
        catalog1 = self.helper.create_catalogus(overrides={"naam": "Catalog 1"})
        catalog2 = self.helper.create_catalogus(overrides={"naam": "Catalog 2"})
        zaaktype1 = self.helper.create_zaaktype()
        zaaktype2 = self.helper.create_zaaktype(
            overrides={
                "catalogus": catalog2.url,
                "broncatalogus": {
                    "url": catalog1.url,
                    "domein": catalog1.domein,
                    "rsin": catalog1.rsin,
                },
                "bronzaaktype": {
                    "url": zaaktype1.url,
                    "identificatie": zaaktype1.identificatie,
                    "omschrijving": zaaktype1.omschrijving,
                },
            }
        )

        assert zaaktype2.url

        zaaktype2_uuid = furl(zaaktype2.url).path.segments[-1]
        self.client.force_login(self.user)

        endpoint = reverse(
            "api:zaaktypen:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": zaaktype2_uuid},
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data["result"]["broncatalogus"],
            {"url": catalog1.url, "domein": catalog1.domein, "rsin": catalog1.rsin},
        )
        self.assertEqual(
            data["result"]["bronzaaktype"],
            {
                "url": zaaktype1.url,
                "identificatie": zaaktype1.identificatie,
                "omschrijving": zaaktype1.omschrijving,
            },
        )

    def test_selectielijst_procestype_options(self):
        zaaktype = self.helper.create_zaaktype()
        endpoint = reverse(
            "api:zaaktypen:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": zaaktype.uuid},
        )

        self.client.force_login(self.user)
        response = self.client.get(endpoint)
        data = response.json()

        ob_field = next(
            (f for f in data["fields"] if f["name"] == "selectielijstProcestype")
        )
        options = ob_field["options"]

        previous = None
        for option in options:
            label = option["label"]
            value = option["value"]
            match = re.search(r"\d{4}", label)
            year = int(match[0]) if match else 0

            previous_label = previous["label"] if previous else ""
            previous_match = re.search(r"\d{4}", previous_label)
            previous_year = int(previous_match[0]) if previous_match else year

            # Label should be present
            self.assertTrue(label)

            # Value should be a URL
            self.assertIn("https://", value)

            # Within same year, should be sorted alphabetically
            if year == previous_year:
                self.assertGreater(label, previous_label)
            # Years should be descending.
            else:
                self.assertLess(year, previous_year)

            previous = option

    def test_retrieve_published_zaaktype(self):
        """
        We need the zaaktype to be pulished, because otherwise we can't
        retrieve the related zaakobjecttypen from openzaak (see issue open-zaak/open-zaak#2178)
        """
        zaaktype = self.helper.create_zaaktype_with_relations(publish=True)

        self.client.force_login(self.user)

        endpoint = reverse(
            "api:zaaktypen:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": zaaktype.uuid},
        )

        self.client.force_login(self.user)

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        zaakobjecttypen = data["result"]["_expand"]["zaakobjecttypen"]

        self.assertEqual(len(zaakobjecttypen), 1)

        zaakobjecttype = zaakobjecttypen[0]

        self.assertIn("_expand", zaakobjecttype)
        self.assertIn("objecttype", zaakobjecttype["_expand"])

        self.assertEqual(
            "Parkeer vergunning", zaakobjecttype["_expand"]["objecttype"]["name"]
        )

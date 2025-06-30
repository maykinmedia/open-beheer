from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from maykin_common.vcr import VCRMixin
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory


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

    def test_not_authenticated(self):
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

        self.assertEqual(len(data["versions"]), 1)

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

        with self.subTest("fields"):
            self.assertEqual(data["fields"][1]["name"], "vertrouwelijkheidaanduiding")
            self.assertEqual(len(data["fields"][1]["options"]), 8)

    def test_patch_zaaktype(self):
        """
        Before re-recording the cassettes for this test, make sure to
        reload the fixtures in the docker container of Open Zaak.
        """
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ce9feadd-00cb-46c8-a0ef-1d1dfc78586a"},
        )
        self.client.force_login(self.user)

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        with self.subTest("Check the value before modifying it"):
            self.assertEqual(
                data["result"]["omschrijving"], "Destruction confirmation type"
            )

        # Now modify the zaaktype
        response = self.client.patch(endpoint, data={"omschrijving": "MODIFIED"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)

        self.assertEqual(len(data["versions"]), 2)

        zaaktype = data["result"]

        with self.subTest("Modified field"):
            self.assertEqual(zaaktype["omschrijving"], "MODIFIED")

        with self.subTest("Not modified fields"):
            self.assertFalse(zaaktype["concept"])
            self.assertEqual(zaaktype["vertrouwelijkheidaanduiding"], "openbaar")
            self.assertEqual(
                zaaktype["doel"],
                "To confirm that a destruction list has been correctly processed.",
            )
            self.assertEqual(
                zaaktype["aanleiding"],
                "When a destructio list is processed by Open Archiefbeheer",
            )
            self.assertEqual(zaaktype["indicatieInternOfExtern"], "extern")
            self.assertEqual(zaaktype["handelingInitiator"], "indienen")
            self.assertEqual(zaaktype["onderwerp"], "Destruction")
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
            self.assertEqual(zaaktype["beginGeldigheid"], "2025-03-21")
            self.assertEqual(zaaktype["versiedatum"], "2018-01-01")
            self.assertEqual(
                zaaktype["catalogus"],
                "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
            )
            self.assertEqual(zaaktype["besluittypen"], [])
            self.assertEqual(zaaktype["gerelateerdeZaaktypen"], [])
            self.assertEqual(
                zaaktype["url"],
                "http://localhost:8003/catalogi/api/v1/zaaktypen/ce9feadd-00cb-46c8-a0ef-1d1dfc78586a",
            )
            self.assertEqual(zaaktype["identificatie"], "ZAAKTYPE-2018-0000000002")
            self.assertEqual(zaaktype["omschrijvingGeneriek"], "")
            self.assertEqual(zaaktype["toelichting"], "")
            self.assertIsNone(zaaktype["servicenorm"])
            self.assertIsNone(zaaktype["verlengingstermijn"])
            self.assertEqual(zaaktype["trefwoorden"], [])
            self.assertEqual(zaaktype["publicatietekst"], "")
            self.assertEqual(zaaktype["verantwoordingsrelatie"], [])
            self.assertEqual(
                zaaktype["selectielijstProcestype"],
                "https://selectielijst.openzaak.nl/api/v1/procestypen/c844637e-6393-4202-b030-e1bffb08a9b0",
            )
            self.assertIsNone(zaaktype["broncatalogus"])
            self.assertIsNone(zaaktype["bronzaaktype"])
            self.assertIsNone(zaaktype["eindeGeldigheid"])
            self.assertEqual(zaaktype["beginObject"], "2018-01-01")
            self.assertIsNone(zaaktype["eindeObject"])
            self.assertEqual(
                zaaktype["statustypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/statustypen/835a2a13-f52f-4339-83e5-b7250e5ad016"
                ],
            )
            self.assertEqual(
                zaaktype["resultaattypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/resultaattypen/5d39b8ac-437a-475c-9a76-0f6ae1540d0e"
                ],
            )
            self.assertEqual(zaaktype["eigenschappen"], [])
            self.assertEqual(
                zaaktype["informatieobjecttypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/informatieobjecttypen/9dee6712-122e-464a-99a3-c16692de5485"
                ],
            )
            self.assertEqual(zaaktype["roltypen"], [])
            self.assertEqual(zaaktype["deelzaaktypen"], [])
            self.assertEqual(zaaktype["zaakobjecttypen"], [])

    def test_put_zaaktype(self):
        """
        Before re-recording the cassettes for this test, make sure to
        reload the fixtures in the docker container of Open Zaak.
        """
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ce9feadd-00cb-46c8-a0ef-1d1dfc78586a"},
        )
        self.client.force_login(self.user)

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        zaaktype = response.json()["result"]

        with self.subTest("Check the values before modifying them"):
            self.assertEqual(zaaktype["omschrijving"], "Destruction confirmation type")
            self.assertFalse(zaaktype["concept"])
            self.assertEqual(zaaktype["vertrouwelijkheidaanduiding"], "openbaar")
            self.assertEqual(
                zaaktype["doel"],
                "To confirm that a destruction list has been correctly processed.",
            )
            self.assertEqual(
                zaaktype["aanleiding"],
                "When a destructio list is processed by Open Archiefbeheer",
            )
            self.assertEqual(zaaktype["indicatieInternOfExtern"], "extern")
            self.assertEqual(zaaktype["handelingInitiator"], "indienen")
            self.assertEqual(zaaktype["onderwerp"], "Destruction")
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
            self.assertEqual(zaaktype["beginGeldigheid"], "2025-03-21")
            self.assertEqual(zaaktype["versiedatum"], "2018-01-01")
            self.assertEqual(
                zaaktype["catalogus"],
                "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
            )
            self.assertEqual(zaaktype["besluittypen"], [])
            self.assertEqual(zaaktype["gerelateerdeZaaktypen"], [])
            self.assertEqual(
                zaaktype["url"],
                "http://localhost:8003/catalogi/api/v1/zaaktypen/ce9feadd-00cb-46c8-a0ef-1d1dfc78586a",
            )
            self.assertEqual(zaaktype["identificatie"], "ZAAKTYPE-2018-0000000002")
            self.assertEqual(zaaktype["omschrijvingGeneriek"], "")
            self.assertEqual(zaaktype["toelichting"], "")
            self.assertIsNone(zaaktype["servicenorm"])
            self.assertIsNone(zaaktype["verlengingstermijn"])
            self.assertEqual(zaaktype["trefwoorden"], [])
            self.assertEqual(zaaktype["publicatietekst"], "")
            self.assertEqual(zaaktype["verantwoordingsrelatie"], [])
            self.assertEqual(
                zaaktype["selectielijstProcestype"],
                "https://selectielijst.openzaak.nl/api/v1/procestypen/c844637e-6393-4202-b030-e1bffb08a9b0",
            )
            self.assertIsNone(zaaktype["broncatalogus"])
            self.assertIsNone(zaaktype["bronzaaktype"])
            self.assertIsNone(zaaktype["eindeGeldigheid"])
            self.assertEqual(zaaktype["beginObject"], "2018-01-01")
            self.assertIsNone(zaaktype["eindeObject"])
            self.assertEqual(
                zaaktype["statustypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/statustypen/835a2a13-f52f-4339-83e5-b7250e5ad016"
                ],
            )
            self.assertEqual(
                zaaktype["resultaattypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/resultaattypen/5d39b8ac-437a-475c-9a76-0f6ae1540d0e"
                ],
            )
            self.assertEqual(zaaktype["eigenschappen"], [])
            self.assertEqual(
                zaaktype["informatieobjecttypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/informatieobjecttypen/9dee6712-122e-464a-99a3-c16692de5485"
                ],
            )
            self.assertEqual(zaaktype["roltypen"], [])
            self.assertEqual(zaaktype["deelzaaktypen"], [])
            self.assertEqual(zaaktype["zaakobjecttypen"], [])

        # Now modify the zaaktype
        response = self.client.put(
            endpoint,
            data={
                "omschrijving": "MODIFIED",
                "vertrouwelijkheidaanduiding": "geheim",
                "doel": "MODIFIED",
                "aanleiding": "MODIFIED",
                "indicatieInternOfExtern": "intern",
                "handelingInitiator": "aanvragen",
                "onderwerp": "MODIFIED",
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("versions", data)
        self.assertIn("result", data)
        self.assertIn("fieldsets", data)

        self.assertEqual(len(data["versions"]), 2)

        zaaktype = data["result"]

        # Now check the modified values
        with self.subTest("Now check the modified values"):
            self.assertEqual(zaaktype["omschrijving"], "MODIFIED")
            self.assertFalse(zaaktype["concept"])
            self.assertEqual(zaaktype["vertrouwelijkheidaanduiding"], "geheim")
            self.assertEqual(
                zaaktype["doel"],
                "MODIFIED",
            )
            self.assertEqual(
                zaaktype["aanleiding"],
                "MODIFIED",
            )
            self.assertEqual(zaaktype["indicatieInternOfExtern"], "intern")
            self.assertEqual(zaaktype["handelingInitiator"], "aanvragen")
            self.assertEqual(zaaktype["onderwerp"], "MODIFIED")
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
            self.assertEqual(
                zaaktype["url"],
                "http://localhost:8003/catalogi/api/v1/zaaktypen/ce9feadd-00cb-46c8-a0ef-1d1dfc78586a",
            )
            self.assertEqual(zaaktype["identificatie"], "ZAAKTYPE-2018-0000000002")
            self.assertEqual(zaaktype["omschrijvingGeneriek"], "")
            self.assertEqual(zaaktype["toelichting"], "")
            self.assertIsNone(zaaktype["servicenorm"])
            self.assertEqual(zaaktype["verlengingstermijn"], "P40D")
            self.assertEqual(zaaktype["trefwoorden"], [])
            self.assertEqual(zaaktype["publicatietekst"], "")
            self.assertEqual(zaaktype["verantwoordingsrelatie"], [])
            self.assertEqual(
                zaaktype["selectielijstProcestype"],
                "https://selectielijst.openzaak.nl/api/v1/procestypen/c844637e-6393-4202-b030-e1bffb08a9b0",
            )
            self.assertIsNone(zaaktype["broncatalogus"])
            self.assertIsNone(zaaktype["bronzaaktype"])
            self.assertIsNone(zaaktype["eindeGeldigheid"])
            self.assertEqual(zaaktype["beginObject"], "2018-01-01")
            self.assertIsNone(zaaktype["eindeObject"])
            self.assertEqual(
                zaaktype["statustypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/statustypen/835a2a13-f52f-4339-83e5-b7250e5ad016"
                ],
            )
            self.assertEqual(
                zaaktype["resultaattypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/resultaattypen/5d39b8ac-437a-475c-9a76-0f6ae1540d0e"
                ],
            )
            self.assertEqual(zaaktype["eigenschappen"], [])
            self.assertEqual(
                zaaktype["informatieobjecttypen"],
                [
                    "http://localhost:8003/catalogi/api/v1/informatieobjecttypen/9dee6712-122e-464a-99a3-c16692de5485"
                ],
            )
            self.assertEqual(zaaktype["roltypen"], [])
            self.assertEqual(zaaktype["deelzaaktypen"], [])
            self.assertEqual(zaaktype["zaakobjecttypen"], [])

    def test_proxy_error_response(self):
        endpoint = reverse(
            "api:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": "ce9feadd-00cb-46c8-a0ef-1d1dfc78586a"},
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

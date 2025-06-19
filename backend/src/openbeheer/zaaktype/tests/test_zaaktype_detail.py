from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from vcr.unittest import VCRMixin
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory


class ZaakTypeListViewTest(VCRMixin, APITestCase):
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

        self.assertEqual(len(data["versions"]), 1)

        zaaktype = data["result"]

        self.assertEqual(zaaktype["omschrijving"], "Testing resultaattypen process")
        self.assertEqual(zaaktype["vertrouwelijkheidaanduiding"], "openbaar")
        self.assertEqual(
            zaaktype["doel"],
            "Trouble red compare produce animal. Everything today Democrat student enter. By probably adult.",
        )
        self.assertEqual(
            zaaktype["aanleiding"], "Couple toward trip old nice memory system instead."
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

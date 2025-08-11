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
class ZaakTypePublishViewTest(VCRMixin, APITestCase):
    vcr_enabled = False

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
            "api:zaaktypen:zaaktype-publish",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertEqual(self.cassette.play_count, 0)

    def test_publish_zaaktype(self):
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

        self.helper.create_statustype(
            overrides={
                "zaaktype": zaaktype.url,
                "omschrijving": "Begin",
                "volgnummer": 1,
            }
        )

        self.helper.create_statustype(
            overrides={
                "zaaktype": zaaktype.url,
                "omschrijving": "Eind",
                "volgnummer": 2,
            }
        )

        assert zaaktype.url
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]
        self.client.force_login(self.user)

        self.assertTrue(zaaktype.concept)

        endpoint = reverse(
            "api:zaaktypen:zaaktype-publish",
            kwargs={"slug": "OZ", "uuid": zaaktype_uuid},
        )
        response = self.client.post(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()

        self.assertFalse(data["concept"])

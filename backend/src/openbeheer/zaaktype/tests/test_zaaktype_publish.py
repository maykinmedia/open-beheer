from furl import furl
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.clients import ztc_client
from openbeheer.config.tests.factories import APIConfigFactory
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import (
    VCRAPITestCase,
    matcher_query_without_datum_geldigheid,
)


class ZaakTypePublishViewTest(VCRAPITestCase):
    custom_matchers = [
        ("query_without_datum_geldigheid", matcher_query_without_datum_geldigheid)
    ]
    custom_match_on = (
        "method",
        "scheme",
        "host",
        "port",
        "path",
        "query_without_datum_geldigheid",
    )

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
            "api:zaaktypen:zaaktype-publish",
            kwargs={"slug": "OZ", "uuid": "ec9ebcdb-b652-466d-a651-fdb8ea787487"},
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_publish_zaaktype(self):
        zaaktype = self.helper.create_zaaktype(
            selectielijstProcestype="https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0"
        )
        assert zaaktype.url
        self.helper.create_resultaattype(
            zaaktype=zaaktype.url,
            omschrijving="Toegekend",
            resultaattypeomschrijving="https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/fb65d251-1518-4185-865f-b8bdcfad07b1",
            selectielijstklasse="https://selectielijst.openzaak.nl/api/v1/resultaten/afa30940-855b-4a7e-aa21-9e15a8078814",
        )
        self.helper.create_resultaattype(
            zaaktype=zaaktype.url,
            omschrijving="Afgehandeld",
            resultaattypeomschrijving="https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/7cb315fb-4f7b-4a43-aca1-e4522e4c73b3",
            selectielijstklasse="https://selectielijst.openzaak.nl/api/v1/resultaten/8af64c99-a168-40dd-8afd-9fbe0597b6dc",
        )
        self.helper.create_roltype(
            zaaktype=zaaktype.url,
            omschrijving="Behandelend afdeling",
            omschrijvingGeneriek="behandelaar",
        )

        self.helper.create_statustype(
            zaaktype=zaaktype.url,
            omschrijving="begin",
            volgnummer=1,
        )

        self.helper.create_statustype(
            zaaktype=zaaktype.url,
            omschrijving="eind",
            volgnummer=2,
        )

        assert zaaktype.url
        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]
        assert zaaktype.concept is True

        self.client.force_login(self.user)

        endpoint = reverse(
            "api:zaaktypen:zaaktype-publish",
            kwargs={"slug": "OZ", "uuid": zaaktype_uuid},
        )
        response = self.client.post(endpoint)

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.content
        )

        detail_endpoint = reverse(
            "api:zaaktypen:zaaktype-detail",
            kwargs={"slug": "OZ", "uuid": zaaktype_uuid},
        )

        detail = self.client.get(detail_endpoint).json()["result"]

        self.assertFalse(detail["concept"])

        deletion_attempt = self.client.delete(detail_endpoint)
        self.assertEqual(
            deletion_attempt.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_publish_zaaktype_404(self):
        self.client.force_login(self.user)
        zaaktype_uuid = "542983d2-78fd-11f0-a844-c3f05b711b08"

        endpoint = reverse(
            "api:zaaktypen:zaaktype-publish",
            kwargs={"slug": "OZ", "uuid": zaaktype_uuid},
        )
        response = self.client.post(endpoint)

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, response.content
        )

    def test_publish_zaaktype_with_unpublished_iot(self):
        self.client.force_login(self.user)
        zaaktype = self.helper.create_zaaktype()
        assert zaaktype.url
        self.helper.create_statustype(
            zaaktype=zaaktype.url,
            omschrijving="begin",
            volgnummer=1,
        )
        self.helper.create_statustype(
            zaaktype=zaaktype.url,
            omschrijving="eind",
            volgnummer=2,
        )
        self.helper.create_roltype(zaaktype=zaaktype.url)
        self.helper.create_resultaattype(zaaktype=zaaktype.url)

        iot = self.helper.create_informatieobjecttype(catalogus=zaaktype.catalogus)
        assert iot.url and iot.concept
        self.helper.relate_zaaktype_informatieobjecttype(zaaktype.url, iot.url)

        zaaktype_uuid = furl(zaaktype.url).path.segments[-1]
        endpoint = reverse(
            "api:zaaktypen:zaaktype-publish",
            kwargs={"slug": "OZ", "uuid": zaaktype_uuid},
        )

        response = self.client.post(endpoint)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with ztc_client() as client:
            client.post(f"{iot.url}/publish")

        response = self.client.post(endpoint)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

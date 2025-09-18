from requests import Timeout
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import VCRAPITestCase


class CatalogiChoicesView(VCRAPITestCase):
    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
            slug="tralala-service",
        )
        response = self.client.get(
            reverse("api:catalogi:choices", kwargs={"slug": "tralala-service"})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_choices(self):
        user = UserFactory.create()
        ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
            slug="tralala-service",
        )

        helper = OpenZaakDataCreationHelper(ztc_service_slug="tralala-service")
        catalogus = helper.create_catalogus(naam="Test Catalogue")
        self.addCleanup(lambda: helper.delete_resource(catalogus))
        self.client.force_login(user)
        response = self.client.get(
            reverse("api:catalogi:choices", kwargs={"slug": "tralala-service"})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertGreaterEqual(len(data), 1)

        self.assertEqual(data[0]["label"], f"Test Catalogue ({catalogus.domein})")
        self.assertEqual(data[0]["value"], catalogus.url)

    def test_openzaak_down(self):
        user = UserFactory.create()
        ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8004/catalogi/api/v1",  # Does not exist, so it's not up
            client_id="test-vcr",
            secret="test-vcr",
            slug="tralala-service",
        )

        self.client.force_login(user)

        with self.vcr_raises(Timeout):
            response = self.client.get(
                reverse("api:catalogi:choices", kwargs={"slug": "tralala-service"})
            )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.json()["code"], "connection_error")

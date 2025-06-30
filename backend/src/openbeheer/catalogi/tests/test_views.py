from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory
from maykin_common.vcr import VCRMixin

from openbeheer.accounts.tests.factories import UserFactory


class CatalogiChoicesView(VCRMixin, APITestCase):
    def test_not_authenticated(self):
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

    def test_retrieve_choices(self):
        user = UserFactory.create()
        ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
            slug="tralala-service",
        )

        self.client.force_login(user)
        response = self.client.get(
            reverse("api:catalogi:choices", kwargs={"slug": "tralala-service"})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["label"], "Test Catalogue (VAVAV)")
        self.assertEqual(
            data[0]["value"],
            "ec77ad39-0954-4aeb-bcf2-6f45263cde77",
        )


class CatalogiChoicesErrorViewTests(APITestCase):
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
        response = self.client.get(
            reverse("api:catalogi:choices", kwargs={"slug": "tralala-service"})
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.json()["code"], "connection_error")

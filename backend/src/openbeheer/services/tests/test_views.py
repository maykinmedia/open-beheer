from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory


class CatalogiChoicesView(APITestCase):
    def test_not_authenticated(self):
        response = self.client.get(reverse("api:services:choices"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_choices(self):
        user = UserFactory.create()
        ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
            slug="tralala-service",
            label="Test Tralala",
        )

        self.client.force_login(user)
        response = self.client.get(reverse("api:services:choices"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["label"], "Test Tralala")
        self.assertEqual(data[0]["value"], "tralala-service")

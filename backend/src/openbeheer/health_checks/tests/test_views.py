from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from openbeheer.accounts.tests.factories import UserFactory


class HealthCheckViewTest(APITestCase):
    def test_not_authenticated(self):
        response = self.client.get(reverse("api:health-checks"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_health_checks(self):
        user = UserFactory.create()

        self.client.force_login(user)
        response = self.client.get(reverse("api:health-checks"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

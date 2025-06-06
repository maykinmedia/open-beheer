from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class ZaakTypeListViewTest(APITestCase):
    def test_not_authenticated(self):
        endpoint = reverse("api:zaaktype-list")

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class CustomExceptionHandlerTest(APITestCase):
    def test_unauthorised_exception(self):
        endpoint = reverse("api:services:choices")

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["code"], "not_authenticated")

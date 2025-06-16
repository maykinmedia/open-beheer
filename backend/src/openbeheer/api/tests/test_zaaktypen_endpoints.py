from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.types import ZGWResponse


class ZaaktypeListTestCase(APITestCase):
    def test_not_authenticated(self):
        url = reverse("api:zaaktype-list", kwargs={"slug": "foo"})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("openbeheer.api.views.ListView.get_data")
    def test_list(self, get_data_mock):
        get_data_mock.return_value = [
            ZGWResponse(count=0, next="", previous="", results=[]),
            200,
        ]

        user = UserFactory.create(username="test", password="test")
        self.client.force_authenticate(user=user)
        url = reverse("api:zaaktype-list", kwargs={"slug": "foo"})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.fields[0].name, "identificatie")
        self.assertEqual(response.data.pagination.count, 0)
        self.assertEqual(response.data.pagination.next, "")
        self.assertEqual(response.data.pagination.previous, "")
        self.assertEqual(response.data.results, [])

    @patch("openbeheer.api.views.ListView.get_data")
    def test_catalog_filter(self, get_data_mock):
        get_data_mock.return_value = [
            ZGWResponse(count=0, next="", previous="", results=[]),
            200,
        ]

        user = UserFactory.create(username="test", password="test")
        self.client.force_authenticate(user=user)
        url = reverse("api:zaaktype-list", kwargs={"slug": "foo"})

        response = self.client.get(url, query_params={"catalogus": "bar"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data_mock.call_args[0][0].catalogus, "bar")

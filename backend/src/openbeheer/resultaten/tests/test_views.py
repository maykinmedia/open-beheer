from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.reverse import reverse

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.config.tests.factories import APIConfigFactory
from openbeheer.utils.tests import VCRAPITestCase


class ResultaatDetailViewTest(VCRAPITestCase):
    user: User
    endpoint_by_url: str
    resultaat_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        APIConfigFactory()
        cls.user = UserFactory.create()
        cls.endpoint_by_url = reverse("api:resultaten:resultaten-detail-by-url")
        cls.resultaat_url = "https://selectielijst.openzaak.nl/api/v1/resultaten/7f838b25-3fc2-4bb7-a6be-5fc52b76df75"

    def test_not_authenticated(self):
        response = self.client.get(
            self.endpoint_by_url, data={"url": self.resultaat_url}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # no service calls made
        assert not self.cassette

    def test_retrieve_resultaat_by_url(self):
        self.client.force_login(self.user)

        response = self.client.get(
            self.endpoint_by_url, data={"url": self.resultaat_url}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        assert set(data.keys()).issuperset({"waardering", "procestermijn"})

    def test_retrieve_resultaat_by_url_with_empty_processtermijn(self):
        self.client.force_login(self.user)

        url = "https://selectielijst.openzaak.nl/api/v1/resultaten/8320ab7d-3a8d-4c8b-b94a-14b4fa374d0a"
        response = self.client.get(self.endpoint_by_url, data={"url": url})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        assert set(data.keys()).issuperset({"waardering", "procestermijn"})
        assert data["procestermijn"] == ""  # is this okay?

    def test_retrieve_resultaat_by_url_without_url(self):
        self.client.force_login(self.user)

        response = self.client.get(self.endpoint_by_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # no service calls made
        assert not self.cassette

    def test_retrieve_resultaat_by_url_is_not_an_open_proxy(self):
        self.client.force_login(self.user)

        url = "https://example.com"
        response = self.client.get(self.endpoint_by_url, data={"url": url})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # no service calls made
        assert not self.cassette

    def test_patch_resultaat(self):
        self.client.force_login(self.user)

        changes = {"omschrijving": "MODIFIED by patch"}

        response = self.client.patch(self.endpoint_by_url, data=changes)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # no service calls made
        assert not self.cassette

    def test_put_resultaat(self):
        self.client.force_login(self.user)

        response = self.client.put(
            self.endpoint_by_url,
            data={"omschrijving": "Not allowed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # no service calls made
        assert not self.cassette

    def test_delete_resultaat(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.endpoint_by_url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # no service calls made
        assert not self.cassette

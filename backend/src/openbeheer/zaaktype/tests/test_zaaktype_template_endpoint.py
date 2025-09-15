from rest_framework import status
from rest_framework.reverse import reverse

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.utils.tests import VCRAPITestCase


class ZaakTypeTemplateListViewTest(VCRAPITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory.create()
        cls.url = reverse("api:zaaktypetemplate-list")

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        data = response.json()

        self.assertGreater(data["count"], 0)

        basis = data["results"][0]

        self.assertEqual(basis["naam"], "Basis")
        self.assertEqual(
            basis["omschrijving"],
            "Start hier een nieuwe zaak met de juiste structuur en vooraf ingevulde velden.",
        )

        self.assertListEqual(
            basis["voorbeelden"],
            [
                "Zelf opbouwen",
                "Volledig zelf te configureren",
                "Vertrouwelijkheidaanduiding: openbaar",
            ],
        )

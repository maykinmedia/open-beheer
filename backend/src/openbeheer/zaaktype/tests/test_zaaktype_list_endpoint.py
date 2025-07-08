from maykin_common.vcr import VCRMixin
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.types.ztc import Status


class ZaakTypeListViewTest(VCRMixin, APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.service = ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
            slug="OZ",
        )
        cls.user = UserFactory.create()
        cls.url = reverse("api:zaaktypen:zaaktype-list", kwargs={"slug": "OZ"})

    def test_not_authenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        data = response.json()

        self.assertGreater(data["pagination"]["count"], 0)

        field_names = {f["name"] for f in data["fields"]}

        # has specced fields
        self.assertSetEqual(
            field_names,
            {
                "url",
                "omschrijving",
                "identificatie",
                "eindeGeldigheid",
                "versiedatum",
                "vertrouwelijkheidaanduiding",
                "actief",
                "concept",
            },
        )

        # all rows have at least all fields
        for row in data["results"]:
            keys_in_fields = set(row.keys()) & field_names
            self.assertSetEqual(keys_in_fields, field_names)

    def test_catalog_filter(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            self.url, query_params={"catalogus": "ec77ad39-0954-4aeb-bcf2-1beefbadf00d"}
        )

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["pagination"]["count"], 0)
        self.assertEqual(data["results"], [])

        response = self.client.get(
            self.url, query_params={"catalogus": "ec77ad39-0954-4aeb-bcf2-6f45263cde77"}
        )

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(data["pagination"]["count"], 0)
        self.assertGreater(len(data["results"]), 0)

    def test_datum_geldigheid_filter(self):
        self.client.force_authenticate(self.user)
        url = reverse("api:zaaktypen:zaaktype-list", kwargs={"slug": "OZ"})

        response = self.client.get(url, query_params={"datumGeldigheid": "2001-01-01"})

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["pagination"]["count"], 0)
        self.assertEqual(data["results"], [])

    def test_page_request(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url, query_params={"page": 1})

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(data["pagination"]["count"], 0)
        self.assertGreater(len(data["results"]), 0)

        self.assertEqual(data["pagination"]["page"], 1)

    def test_status_filter(self):
        self.client.force_authenticate(self.user)

        for status_param in Status:
            with self.subTest(f"{status_param=}"):
                response = self.client.get(
                    self.url, query_params={"status": status_param.value}
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_identificatie_filter(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            self.url, query_params={"identificatie": "ZAAKTYPE-2018-0000000001"}
        )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(data["pagination"]["count"], 0)
        self.assertGreater(len(data["results"]), 0)

        self.assertSetEqual(
            {r["identificatie"] for r in data["results"]}, {"ZAAKTYPE-2018-0000000001"}
        )

    def test_trefwoorden_filter_single_word(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url, query_params={"trefwoorden": "foo"})

        response.json()  # TODO: Add some to the fixtures?

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_trefwoorden_filter_multi_word(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url, query_params={"trefwoorden": "foo,bar"})

        response.json()  # TODO: Add some to the fixtures?

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ZaakTypeCreateViewTest(VCRMixin, APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.service = ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
            slug="OZ",
        )
        cls.user = UserFactory.create()
        cls.url = reverse("api:zaaktypen:zaaktype-list", kwargs={"slug": "OZ"})

    def test_create_zaaktype(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            data={
                "omschrijving": "New Zaaktype 001",
                "vertrouwelijkheidaanduiding": "geheim",
                "doel": "New Zaaktype 001",
                "aanleiding": "New Zaaktype 001",
                "indicatieInternOfExtern": "intern",
                "handelingInitiator": "aanvragen",
                "onderwerp": "New Zaaktype 001",
                "handelingBehandelaar": "handelin",
                "doorlooptijd": "P40D",
                "opschortingEnAanhoudingMogelijk": False,
                "verlengingMogelijk": True,
                "verlengingstermijn": "P40D",
                "publicatieIndicatie": False,
                "productenOfDiensten": ["https://example.com/product/321"],
                "referentieproces": {"naam": "ReferentieProces 1"},
                "verantwoordelijke": "200000000",
                "beginGeldigheid": "2025-06-19",
                "versiedatum": "2025-06-19",
                "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
                "besluittypen": [],
                "gerelateerdeZaaktypen": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_missing_data(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            data={
                # "omschrijving": "New Zaaktype 001", # Missing!
                "vertrouwelijkheidaanduiding": "geheim",
                "doel": "New Zaaktype 001",
                "aanleiding": "New Zaaktype 001",
                "indicatieInternOfExtern": "intern",
                "handelingInitiator": "aanvragen",
                "onderwerp": "New Zaaktype 001",
                "handelingBehandelaar": "handelin",
                "doorlooptijd": "P40D",
                "opschortingEnAanhoudingMogelijk": False,
                "verlengingMogelijk": True,
                "verlengingstermijn": "P40D",
                "publicatieIndicatie": False,
                "productenOfDiensten": ["https://example.com/product/321"],
                "referentieproces": {"naam": "ReferentieProces 1"},
                "verantwoordelijke": "200000000",
                "beginGeldigheid": "2025-06-19",
                "versiedatum": "2025-06-19",
                "catalogus": "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
                "besluittypen": [],
                "gerelateerdeZaaktypen": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["invalidParams"][0]["name"], "omschrijving")
        self.assertEqual(response.json()["invalidParams"][0]["code"], "required")

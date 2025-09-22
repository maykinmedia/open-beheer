from msgspec import to_builtins
from rest_framework import status
from rest_framework.reverse import reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.config.tests.factories import APIConfigFactory
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
from openbeheer.utils.tests import VCRAPITestCase


class ZaakTypeInformatieObjectTypeListViewTests(VCRAPITestCase):
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
        APIConfigFactory.create()
        cls.user = UserFactory.create()
        cls.helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")

    def test_not_authenticated(self):
        zaaktype = self.helper.create_zaaktype()

        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        endpoint = reverse(
            "api:zaaktype-informatieobjecttypen:zaaktype-informatieobjecttypen-list",
            kwargs={
                "slug": "OZ",
                "zaaktype": zaaktype.uuid,
            },
        )
        response = self.client.get(endpoint, params={"zaaktype": zaaktype.url})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_zaaktype_informatieobjecttypen(self):
        zaaktype = self.helper.create_zaaktype()
        informatieobjecttype = self.helper.create_informatieobjecttype(
            catalogus=zaaktype.catalogus
        )
        assert zaaktype.url and informatieobjecttype.url
        ztiot = self.helper.relate_zaaktype_informatieobjecttype(
            zaaktype_url=zaaktype.url, informatieobjecttype_url=informatieobjecttype.url
        )

        self.client.force_login(self.user)
        endpoint = reverse(
            "api:zaaktype-informatieobjecttypen:zaaktype-informatieobjecttypen-list",
            kwargs={
                "slug": "OZ",
                "zaaktype": zaaktype.uuid,
            },
        )
        response = self.client.get(endpoint, params={"zaaktype": zaaktype.uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["url"], ztiot.url)

    def test_create(self):
        zaaktype = self.helper.create_zaaktype()
        informatieobjecttype = self.helper.create_informatieobjecttype(
            catalogus=zaaktype.catalogus
        )

        self.client.force_login(self.user)
        endpoint = reverse(
            "api:zaaktype-informatieobjecttypen:zaaktype-informatieobjecttypen-list",
            kwargs={
                "slug": "OZ",
                "zaaktype": zaaktype.uuid,
            },
        )
        response = self.client.post(
            endpoint,
            data={
                "zaaktype": zaaktype.url,
                "informatieobjecttype": informatieobjecttype.url,
                "volgnummer": 1,
                "richting": "inkomend",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["zaaktype"], zaaktype.url)
        self.assertEqual(data["informatieobjecttype"], informatieobjecttype.url)


class ZaakTypeInformatieObjectTypeDetailViewTest(VCRAPITestCase):
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
        APIConfigFactory.create()
        cls.user = UserFactory.create()

        cls.helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")

    def setUp(self):
        super().setUp()

        self.zaaktype = self.helper.create_zaaktype()
        self.iot = self.helper.create_informatieobjecttype(
            catalogus=self.zaaktype.catalogus
        )
        assert self.zaaktype.url and self.iot.url
        self.ztiot = self.helper.relate_zaaktype_informatieobjecttype(
            zaaktype_url=self.zaaktype.url, informatieobjecttype_url=self.iot.url
        )

    def test_not_authenticated(self):
        calls_during_setup = len(self.cassette.requests) if self.cassette else 0
        endpoint = reverse(
            "api:zaaktype-informatieobjecttypen:zaaktype-informatieobjecttypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
                "uuid": self.ztiot.uuid,
            },
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if self.cassette:
            # These should be no requests to the backend if unauthenticated
            assert len(self.cassette.requests) == calls_during_setup

    def test_retrieve_zaaktype_informatieobjecttype(self):
        self.client.force_login(self.user)

        endpoint = reverse(
            "api:zaaktype-informatieobjecttypen:zaaktype-informatieobjecttypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": self.zaaktype.uuid,
                "uuid": self.ztiot.uuid,
            },
        )
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        result_keys = set(data.keys())

        assert result_keys == {
            "uuid",
            "zaaktype",
            "informatieobjecttype",
            "volgnummer",
            "richting",
            "url",
            "zaaktypeIdentificatie",
            "statustype",
            "catalogus",
        }

    def test_patch_zaaktype_informatieobjecttype(self):
        zaaktype = self.helper.create_zaaktype()
        iot = self.helper.create_informatieobjecttype(catalogus=zaaktype.catalogus)
        assert zaaktype.url and iot.url
        ztiot = self.helper.relate_zaaktype_informatieobjecttype(
            zaaktype_url=zaaktype.url, informatieobjecttype_url=iot.url
        )

        self.client.force_login(self.user)

        changes = {"richting": "inkomend"}

        endpoint = reverse(
            "api:zaaktype-informatieobjecttypen:zaaktype-informatieobjecttypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": zaaktype.uuid,
                "uuid": ztiot.uuid,
            },
        )
        response = self.client.patch(endpoint, data=changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        data = response.json()
        expected = to_builtins(ztiot) | changes
        self.assertEqual(data, expected)

    def test_put_zaaktype_informatieobjecttype(self):
        self.client.force_login(self.user)
        zaaktype = self.helper.create_zaaktype()
        iot = self.helper.create_informatieobjecttype(catalogus=zaaktype.catalogus)
        assert zaaktype.url and iot.url
        ztiot = self.helper.relate_zaaktype_informatieobjecttype(
            zaaktype_url=zaaktype.url,
            informatieobjecttype_url=iot.url,
            richting="inkomend",
            volgnummer=1,
        )

        endpoint = reverse(
            "api:zaaktype-informatieobjecttypen:zaaktype-informatieobjecttypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": zaaktype.uuid,
                "uuid": ztiot.uuid,
            },
        )
        response = self.client.put(
            endpoint,
            data={
                "zaaktype": zaaktype.url,
                "informatieobjecttype": iot.url,
                "volgnummer": 500,
                "richting": "uitgaand",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["zaaktype"], zaaktype.url)
        self.assertEqual(data["informatieobjecttype"], iot.url)
        self.assertEqual(data["volgnummer"], 500)
        self.assertEqual(data["richting"], "uitgaand")

    def test_delete_zaaktype_informatieobjecttype(self):
        self.client.force_login(self.user)
        zaaktype = self.helper.create_zaaktype()
        iot = self.helper.create_informatieobjecttype(catalogus=zaaktype.catalogus)
        assert zaaktype.url and iot.url
        ztiot = self.helper.relate_zaaktype_informatieobjecttype(
            zaaktype_url=zaaktype.url,
            informatieobjecttype_url=iot.url,
            richting="inkomend",
            volgnummer=1,
        )

        endpoint = reverse(
            "api:zaaktype-informatieobjecttypen:zaaktype-informatieobjecttypen-detail",
            kwargs={
                "slug": "OZ",
                "zaaktype": zaaktype.uuid,
                "uuid": ztiot.uuid,
            },
        )
        self.client.force_login(self.user)

        response = self.client.delete(endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

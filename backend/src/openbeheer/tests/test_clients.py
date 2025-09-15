from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from ape_pie import APIClient
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.config.models import APIConfig
from openbeheer.config.tests.factories import APIConfigFactory

from ..clients import selectielijst_client, ztc_client


@override_settings(SOLO_CACHE="default")
class ClientsTests(TestCase):
    def setUp(self):
        ztc_client.cache_clear()
        self.addCleanup(ztc_client.cache_clear)
        selectielijst_client.cache_clear()
        self.addCleanup(selectielijst_client.cache_clear)
        APIConfig.get_solo().delete()
        self.addCleanup(lambda: APIConfig.get_solo().delete())

    def test_no_services_configured_raises_error(self):
        with self.assertRaises(ImproperlyConfigured):
            ztc_client()

        with self.assertRaises(ImproperlyConfigured):
            selectielijst_client()

    def test_get_default(self):
        ServiceFactory.create(api_type=APITypes.ztc)

        client = ztc_client()
        self.assertTrue(isinstance(client, APIClient))

    def test_get_by_slug(self):
        service = ServiceFactory.create(
            api_type=APITypes.ztc, slug="slurm", api_root="https://example.com/futurama"
        )

        client = ztc_client("slurm")
        self.assertTrue(isinstance(client, APIClient))
        self.assertEqual(client.base_url, service.api_root)

    def test_cache_invalidation(self):
        service = ServiceFactory.create(
            api_type=APITypes.ztc, slug="slurm", api_root="https://example.com/futurama"
        )

        client = ztc_client("slurm")

        self.assertTrue(isinstance(client, APIClient))
        self.assertEqual(client.base_url, service.api_root)

        service.api_root = "https://example.com/good_news"

        client2 = ztc_client("slurm")
        self.assertIs(client, client2)

        service.save()

        client3 = ztc_client("slurm")
        self.assertIsNot(client, client3)
        self.assertEqual(client3.base_url, service.api_root)

    def test_selectielijst_client_cache(self):
        APIConfigFactory.create()

        client = selectielijst_client()
        client2 = selectielijst_client()

        assert client is client2

    def test_configuring_different_service_invalidates_selectielijst_client_cache(self):
        config = APIConfigFactory.create()

        initial = selectielijst_client()

        config.selectielijst_api_service = ServiceFactory.create(
            api_root="https://example.com/something-completely-different/"
        )
        config.save()

        client = selectielijst_client()

        assert client is not initial
        assert client.base_url == "https://example.com/something-completely-different/"

    def test_deleting_configured_service_invalidates_selectielijst_client_cache(self):
        config = APIConfigFactory.create()

        initial = selectielijst_client()
        assert initial

        config.selectielijst_api_service.delete()

        with self.assertRaises(ImproperlyConfigured):
            selectielijst_client()

    def test_reconfigured_service_invalidates_selectielijst_client_cache(self):
        config = APIConfigFactory.create()

        initial = selectielijst_client()
        assert initial

        config.selectielijst_api_service = None
        config.save()

        with self.assertRaises(ImproperlyConfigured):
            selectielijst_client()

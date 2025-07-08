from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from ape_pie import APIClient
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from ..clients import ztc_client


class ClientsTests(TestCase):
    def setUp(self):
        self.addCleanup(ztc_client.cache_clear)

    def test_no_services_configured_raises_error(self):
        with self.assertRaises(ImproperlyConfigured):
            ztc_client()

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

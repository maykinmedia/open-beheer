import logging
from importlib import import_module
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import clear_url_caches, include, path

from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.test import APIClient

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.api.catalogi import register_catalogi


class RegisterCatalogiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(SERVICE_OAS=None)
    def test_skips_when_service_oas_not_set(self):
        router = DefaultRouter()
        with self.assertLogs("openbeheer.api.catalogi", level=logging.WARNING) as logs:
            register_catalogi(router)
        self.assertEqual(router.registry, [])
        self.assertIn("SERVICE_OAS not configured", "\n".join(logs.output))

    @override_settings(SERVICE_OAS="http://mock-oas", SERVICE_TYPE="ztc")
    @patch("openbeheer.api.catalogi.get_oas_paths")
    @patch("openbeheer.api.base.viewsets.ZGWViewSet.service_request")
    def test_list_catalogi_registered(self, service_request, mock_get_oas_paths):
        with self.assertLogs("openbeheer.api.catalogi", level=logging.INFO):
            service_request.return_value = Response(status=200)
            mock_get_oas_paths.return_value = ["fruittypen"]

            router = DefaultRouter()
            register_catalogi(router)

            urlconf = import_module(settings.ROOT_URLCONF)
            original_urlpatterns = urlconf.urlpatterns
            urlconf.urlpatterns = [path("", include(router.urls))]

            clear_url_caches()

            try:
                self.client.force_authenticate(user=UserFactory())
                response = self.client.get("/catalogi/fruittypen/")
                self.assertEqual(response.status_code, 200)
            finally:
                urlconf.urlpatterns = original_urlpatterns
                clear_url_caches()

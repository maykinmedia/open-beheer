from pathlib import Path

from django.conf import settings

from django_setup_configuration.runner import SetupConfigurationRunner
from mozilla_django_oidc_db.models import OIDCClient, OIDCProvider
from zgw_consumers.models import Service

from openbeheer.utils.tests import VCRAPITestCase

from ...models import APIConfig

TEST_FILES = (Path(__file__).parent / "files").resolve()
CONFIG_FILE_PATH = str(TEST_FILES / "full_config.yaml")

FIXTURES_FOLDER = (Path(__file__).parent.parent / "fixtures").resolve()
FIXTURE_PATH = str(FIXTURES_FOLDER / "data.yaml")


class APIConfigConfigurationStepTests(VCRAPITestCase):
    def test_full_configuration_no_call_to_keycloak(self):
        runner = SetupConfigurationRunner(
            steps=settings.SETUP_CONFIGURATION_STEPS, yaml_source=CONFIG_FILE_PATH
        )
        # Validate that the configuration settings can be loaded from the source
        runner.validate_all_requirements()

        # Execute all steps
        runner.execute_all()

        services = Service.objects.all()

        self.assertEqual(3, services.count())
        self.assertTrue(services.filter(slug="objecttypen-service").exists())
        self.assertTrue(services.filter(slug="catalogi-service").exists())
        self.assertTrue(services.filter(slug="selectielijst-service").exists())

        api_config = APIConfig.get_solo()

        self.assertEqual(
            api_config.selectielijst_api_service,
            services.get(slug="selectielijst-service"),
        )
        self.assertEqual(
            api_config.objecttypen_api_service, services.get(slug="objecttypen-service")
        )

        oidc_providers = OIDCProvider.objects.all()

        self.assertEqual(1, oidc_providers.count())
        self.assertTrue(oidc_providers[0].identifier, "admin-oidc-provider")

        oidc_clients = OIDCClient.objects.all()

        self.assertEqual(1, oidc_clients.count())
        self.assertTrue(oidc_clients[0].identifier, " admin-oidc")
        self.assertTrue(
            oidc_clients[0].oidc_provider.identifier, " admin-oidc-provider"
        )

    def test_full_configuration_with_call_to_keycloak(self):
        # This test uses the discovery endpoint of Keycloak for configuration, so it
        # will make a call to the discovery endpoint.
        runner = SetupConfigurationRunner(
            steps=settings.SETUP_CONFIGURATION_STEPS, yaml_source=FIXTURE_PATH
        )
        # Validate that the configuration settings can be loaded from the source
        runner.validate_all_requirements()

        # Execute all steps
        runner.execute_all()

        services = Service.objects.all()

        self.assertEqual(3, services.count())
        self.assertTrue(services.filter(slug="objecttypen-service").exists())
        self.assertTrue(services.filter(slug="catalogi-service").exists())
        self.assertTrue(services.filter(slug="selectielijst-service").exists())

        api_config = APIConfig.get_solo()

        self.assertEqual(
            api_config.selectielijst_api_service,
            services.get(slug="selectielijst-service"),
        )
        self.assertEqual(
            api_config.objecttypen_api_service, services.get(slug="objecttypen-service")
        )

        oidc_providers = OIDCProvider.objects.all()

        self.assertEqual(1, oidc_providers.count())
        self.assertTrue(oidc_providers[0].identifier, "admin-oidc-provider")

        oidc_clients = OIDCClient.objects.all()

        self.assertEqual(1, oidc_clients.count())
        self.assertTrue(oidc_clients[0].identifier, " admin-oidc")
        self.assertTrue(
            oidc_clients[0].oidc_provider.identifier, " admin-oidc-provider"
        )

from unittest.mock import patch

from django.test import TestCase
from django.utils.translation import gettext as _

from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from ..health_checks import APIConfigHealthCheck
from ..models import APIConfig


class HealthCheckTests(TestCase):
    def test_no_selectielijst_service(self):
        with patch(
            "openbeheer.config.health_checks.APIConfig.get_solo",
            return_value=APIConfig(selectielijst_api_service=None),
        ):
            check = APIConfigHealthCheck()
            result = check.run()

        self.assertFalse(result.success)

        errors = result.errors
        assert errors

        self.assertEqual(errors[0].code, "missing_selectielijst_api")
        self.assertEqual(
            errors[0].message,
            _(
                "Within API configuration, the Selectielijst API service is not selected."
            ),
        )
        self.assertEqual(errors[0].severity, "error")
        self.assertEqual(errors[0].exc, "")

    def test_selectielijst_service_configured(self):
        service = ServiceFactory.create(
            api_type=APITypes.orc, api_root="https://selectielijst.openzaak.nl/api/v1/"
        )
        with patch(
            "openbeheer.config.health_checks.APIConfig.get_solo",
            return_value=APIConfig(selectielijst_api_service=service),
        ):
            check = APIConfigHealthCheck()
            result = check.run()

        self.assertTrue(result.success)

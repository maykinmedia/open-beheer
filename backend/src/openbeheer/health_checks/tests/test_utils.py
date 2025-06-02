from unittest.mock import patch

from django.test import TestCase, tag
from django.utils.translation import gettext as _

from vcr.unittest import VCRMixin
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.config.models import APIConfig

from ..utils import run_health_checks


@tag("vcr")
class RunningHealthChecksTests(VCRMixin, TestCase):
    def test_everything_configured_correctly(self):
        ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
        )
        service = ServiceFactory.create(
            api_type=APITypes.orc, api_root="https://selectielijst.openzaak.nl/api/v1/"
        )

        with patch(
            "openbeheer.config.health_checks.APIConfig.get_solo",
            return_value=APIConfig(selectielijst_api_service=service),
        ):
            results = run_health_checks()

        for item in results:
            with self.subTest(item["check"]):
                self.assertTrue(item["success"])

    def test_configuration_errors_with_traceback(self):
        ServiceFactory.create(
            label="ZTC",
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1/WRONG",  # Wrong configuration
            client_id="test-vcr",
            secret="test-vcr",
        )
        ServiceFactory.create(
            label="Selectielijst",
            api_type=APITypes.orc,
            api_root="https://selectielijst.openzaak.nl/api/v1/",
        )

        with patch(
            "openbeheer.config.health_checks.APIConfig.get_solo",
            return_value=APIConfig(
                selectielijst_api_service=None
            ),  # No selectielijst configured
        ):
            results = run_health_checks(with_traceback=True)

        self.assertEqual(len(results), 3)

        self.assertFalse(results[0]["success"])
        self.assertEqual(len(results[0]["errors"]), 1)
        self.assertEqual(
            results[0]["errors"][0]["message"],
            _('Service "{service}" is improperly configured.').format(service="ZTC"),
        )
        self.assertEqual("", results[0]["errors"][0].get("traceback"))

        self.assertFalse(results[1]["success"])
        self.assertEqual(len(results[1]["errors"]), 1)
        self.assertEqual(
            results[1]["errors"][0]["message"],
            _(
                'Received unexpected error response from catalogussen endpoint with service "{service}".'
            ).format(service="ZTC"),
        )
        self.assertIn("404 Client Error", results[1]["errors"][0].get("traceback", ""))

        self.assertFalse(results[2]["success"])
        self.assertEqual(len(results[2]["errors"]), 1)
        self.assertEqual(
            results[2]["errors"][0]["message"],
            _(
                "Withing API configuration, the Selectielijst API service is not selected."
            ),
        )
        self.assertEqual("", results[2]["errors"][0].get("traceback"))

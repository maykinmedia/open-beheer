from django.utils.translation import gettext as _

from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.config.tests.factories import APIConfigFactory
from openbeheer.utils.tests import VCRTestCase

from ..utils import run_health_checks


class RunningHealthChecksTests(VCRTestCase):
    def test_everything_configured_correctly(self):
        ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
        )
        service_selectielijst = ServiceFactory.create(
            api_type=APITypes.orc, api_root="https://selectielijst.openzaak.nl/api/v1/"
        )
        service_objecttypes = ServiceFactory.create(
            api_type=APITypes.orc,
            api_root="http://localhost:8004/api/v2/",
            auth_type=AuthTypes.api_key,
            header_key="Authorization",
            header_value="Token 18b2b74ef994314b84021d47b9422e82b685d82f",
        )
        APIConfigFactory.create(
            objecttypen_api_service=service_objecttypes,
            selectielijst_api_service=service_selectielijst,
        )

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

        # No selectielijst configured
        APIConfigFactory.create(
            objecttypen_api_service=None, selectielijst_api_service=None
        )

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
        self.assertEqual(len(results[2]["errors"]), 2)
        self.assertEqual(
            results[2]["errors"][0]["message"],
            _(
                "Within API configuration, the Selectielijst API service is not selected."
            ),
        )
        self.assertEqual("", results[2]["errors"][0].get("traceback"))
        self.assertEqual(
            results[2]["errors"][1]["message"],
            _("Within API configuration, the Objecttypes API service is not selected."),
        )
        self.assertEqual("", results[2]["errors"][1].get("traceback"))

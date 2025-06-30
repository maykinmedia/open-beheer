from io import StringIO

from django.core.management import call_command

from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from maykin_common.vcr import VCRTestCase


class HealthCheckManagementTest(VCRTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        ServiceFactory.create(
            label="ZTC",
            api_type=APITypes.ztc,
            # fail both service and catalogue check
            api_root="http://localhost:8003/catalogi/api/v0-alpha-non-existent/",
            client_id="test-vcr",
            secret="test-vcr",
        )

    def test_without_traceback(self):
        out = StringIO()

        call_command("health_checks", stdout=out)

        command_output = out.getvalue()

        self.assertIn("Services: fail", command_output)
        self.assertIn("Catalogue present: fail", command_output)
        self.assertIn("API configuration: fail", command_output)
        self.assertNotIn("Traceback", command_output)

    def test_with_traceback(self):
        out = StringIO()

        call_command("health_checks", "--with-traceback", stdout=out)

        command_output = out.getvalue()

        self.assertIn("Services: fail", command_output)
        self.assertIn("Catalogue present: fail", command_output)
        self.assertIn("Traceback", command_output)
        self.assertIn("API configuration: fail", command_output)

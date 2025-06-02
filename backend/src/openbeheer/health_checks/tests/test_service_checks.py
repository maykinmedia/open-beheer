from django.test import TestCase, tag
from django.utils.translation import gettext as _

from vcr.unittest import VCRMixin
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from ..checks import CatalogueHealthCheck, ServiceHealthCheck


@tag("vcr")
class ServiceCheckTests(VCRMixin, TestCase):
    def test_ztc_and_orc_services_configured(self):
        ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
        )
        ServiceFactory.create(
            api_type=APITypes.orc, api_root="https://selectielijst.openzaak.nl/api/v1/"
        )

        check = ServiceHealthCheck()
        result = check.run()

        self.assertTrue(result.success)
        self.assertEqual(result.errors, [])

    def test_services_not_configured(self):
        check = ServiceHealthCheck()
        result = check.run()

        self.assertFalse(result.success)

        errors = result.errors
        assert errors

        self.assertEqual(len(errors), 2)

        self.assertEqual(errors[0].code, "missing_service")
        self.assertEqual(
            errors[0].message,
            _('Missing service of type "{service_type}".').format(
                service_type=APITypes.ztc
            ),
        )
        self.assertEqual(errors[0].severity, "error")
        self.assertEqual(errors[0].exc, "")

        self.assertEqual(errors[1].code, "missing_service")
        self.assertEqual(
            errors[1].message,
            _('Missing service of type "{service_type}".').format(
                service_type=APITypes.orc
            ),
        )
        self.assertEqual(errors[1].severity, "error")
        self.assertEqual(errors[1].exc, "")

    def test_services_badly_configured(self):
        ServiceFactory.create(
            label="ZTC",
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1/WRONG",  # Wrong API root
            client_id="test-vcr",
            secret="test-vcr",
        )
        ServiceFactory.create(
            label="Selectielijst",
            api_type=APITypes.orc,
            api_root="https://selectielijst.openzaak.nl/api/v1/WRONG",  # Wrong API root
        )

        check = ServiceHealthCheck()
        result = check.run()

        self.assertFalse(result.success)

        errors = result.errors

        assert errors

        self.assertEqual(len(errors), 2)

        self.assertEqual(errors[0].code, "improperly_configured_service")
        self.assertEqual(
            errors[0].message,
            _('Service "{service}" is improperly configured.').format(service="ZTC"),
        )
        self.assertEqual(errors[0].severity, "error")
        self.assertEqual(errors[0].exc, "")

        self.assertEqual(errors[1].code, "improperly_configured_service")
        self.assertEqual(
            errors[1].message,
            _('Service "{service}" is improperly configured.').format(
                service="Selectielijst"
            ),
        )
        self.assertEqual(errors[1].severity, "error")
        self.assertEqual(errors[1].exc, "")


@tag("vcr")
class CatalogueCheckTests(VCRMixin, TestCase):
    def test_catalogue_configured(self):
        ServiceFactory.create(
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1",
            client_id="test-vcr",
            secret="test-vcr",
        )

        check = CatalogueHealthCheck()
        result = check.run()

        self.assertTrue(result.success)

    def test_no_service_configured(self):
        check = CatalogueHealthCheck()
        result = check.run()

        self.assertFalse(result.success)

        errors = result.errors
        assert errors

        self.assertEqual(errors[0].code, "no_ztc_error")
        self.assertEqual(errors[0].message, _("No ZTC services configured."))
        self.assertEqual(errors[0].severity, "error")
        self.assertEqual(errors[0].exc, "")

    def test_badly_configured_service(self):
        ServiceFactory.create(
            label="ZTC",
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1/WRONG",  # Wrong API Type
            client_id="test-vcr",
            secret="test-vcr",
        )

        check = CatalogueHealthCheck()
        result = check.run()

        self.assertFalse(result.success)

        errors = result.errors
        assert errors

        self.assertEqual(errors[0].code, "response_error")
        self.assertEqual(
            errors[0].message,
            _(
                "Received unexpected error response from "
                'catalogussen endpoint with service "{service}".'
            ).format(service="ZTC"),
        )
        self.assertEqual(errors[0].severity, "error")
        self.assertIn("404 Client Error", errors[0].exc)

    def test_openzaak_down(self):
        """When re-recording the cassettes, kill open-zaak for this test."""
        ServiceFactory.create(
            label="ZTC",
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1/",
            client_id="test-vcr",
            secret="test-vcr",
        )

        check = CatalogueHealthCheck()
        result = check.run()

        self.assertFalse(result.success)

        errors = result.errors
        assert errors

        self.assertEqual(errors[0].code, "connection_error")
        self.assertEqual(
            errors[0].message,
            _('Could not retrieve catalogues with service "{service}".').format(
                service="ZTC"
            ),
        )
        self.assertEqual(errors[0].severity, "error")
        self.assertIn("ConnectionError", errors[0].exc)

    def test_no_catalogue(self):
        """When re-recording cassettes, spin up an openzaak without any catalogi resources."""
        ServiceFactory.create(
            label="ZTC",
            api_type=APITypes.ztc,
            api_root="http://localhost:8003/catalogi/api/v1/",
            client_id="test-vcr",
            secret="test-vcr",
        )

        check = CatalogueHealthCheck()
        result = check.run()

        self.assertFalse(result.success)

        errors = result.errors
        assert errors

        self.assertEqual(errors[0].code, "no_catalogi_error")
        self.assertEqual(
            errors[0].message,
            _(
                'No catalogues returned from catalogussen endpoint with service "{service}".'
            ).format(service="ZTC"),
        )
        self.assertEqual(errors[0].severity, "warning")
        self.assertEqual(errors[0].exc, "")

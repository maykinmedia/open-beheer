from django.test import TestCase
from django.utils.translation import gettext as _

from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.config.tests.factories import APIConfigFactory

from ..health_checks import APIConfigHealthCheck


class HealthCheckTests(TestCase):
    def test_no_selectielijst_service(self):
        APIConfigFactory.create(selectielijst_api_service=None)

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
        APIConfigFactory.create(selectielijst_api_service=service)

        check = APIConfigHealthCheck()
        result = check.run()

        self.assertTrue(result.success)

    def test_no_objecttypes_service(self):
        APIConfigFactory.create(objecttypen_api_service=None)

        check = APIConfigHealthCheck()
        result = check.run()

        self.assertFalse(result.success)

        errors = result.errors
        assert errors

        self.assertEqual(errors[0].code, "missing_objecttype_api")
        self.assertEqual(
            errors[0].message,
            _("Within API configuration, the Objecttypes API service is not selected."),
        )
        self.assertEqual(errors[0].severity, "error")
        self.assertEqual(errors[0].exc, "")

    def test_objecttypes_service_configured(self):
        service = ServiceFactory.create(
            api_type=APITypes.orc, api_root="https://objecttypes.nl/api/v1/"
        )
        APIConfigFactory.create(objecttypen_api_service=service)

        check = APIConfigHealthCheck()
        result = check.run()

        self.assertTrue(result.success)

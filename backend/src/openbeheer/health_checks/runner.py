import traceback

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from .checks import HealthCheck
from .types import HealthCheckError, HealthCheckResult


class HealthChecksRunner:
    """Utility class to run health checks."""

    def _get_checks(self) -> list[HealthCheck]:
        initialised_checks = []
        for check_class_str in settings.HEALTH_CHECKS:
            check_class = import_string(check_class_str)

            check = check_class()
            initialised_checks.append(check)
        return initialised_checks

    def run_checks(self) -> list[HealthCheckResult]:
        # Get the checks that are configured to run
        checks = self._get_checks()

        # Run them and collect the results
        results = []
        for check in checks:
            try:
                result = check.run()
            except Exception:
                result = HealthCheckResult(
                    check=check,
                    errors=[
                        HealthCheckError(
                            code="unknown_error",
                            message=_("An unknown error has occurred."),
                            severity="error",
                            exc=traceback.format_exc(),
                        )
                    ],
                    success=False,
                )
            results.append(result)

        return results

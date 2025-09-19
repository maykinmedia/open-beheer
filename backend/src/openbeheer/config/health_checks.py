from django.utils.translation import gettext_lazy as _

from openbeheer.config.models import APIConfig
from openbeheer.health_checks.checks import HealthCheck
from openbeheer.health_checks.types import HealthCheckError, HealthCheckResult


class APIConfigHealthCheck(HealthCheck):
    human_name = _("API configuration")

    def run(self) -> HealthCheckResult:
        errors = []

        api_config = APIConfig.get_solo()
        if not api_config.selectielijst_api_service:
            errors.append(
                HealthCheckError(
                    code="missing_selectielijst_api",
                    message=_(
                        "Within API configuration, the Selectielijst API service is not selected."
                    ),
                    severity="error",
                )
            )

        if not api_config.objecttypen_api_service:
            errors.append(
                HealthCheckError(
                    code="missing_objecttype_api",
                    message=_(
                        "Within API configuration, the Objecttypes API service is not selected."
                    ),
                    severity="error",
                )
            )

        result = HealthCheckResult(check=self, errors=errors)
        return result

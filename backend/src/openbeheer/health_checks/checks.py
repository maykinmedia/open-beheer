import traceback
from abc import ABC, abstractmethod

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from requests.exceptions import ConnectionError, HTTPError
from zgw_consumers.client import build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from .types import HealthCheckError, HealthCheckResult


class HealthCheck(ABC):
    def get_name(self):
        return self.__class__.__name__

    @abstractmethod
    def run(self) -> HealthCheckResult: ...


class ServiceHealthCheck(HealthCheck):
    def get_name(self) -> str:
        return _("Services")

    def run(self) -> HealthCheckResult:
        errors = []

        for needed_service_type in settings.ZGW_REQUIRED_SERVICE_TYPES:
            service = Service.objects.filter(api_type=needed_service_type).first()

            if not service:
                errors.append(
                    HealthCheckError(
                        code="missing_service",
                        message=_('Missing service of type "{service_type}".').format(
                            service_type=needed_service_type
                        ),
                        severity="error",
                    )
                )
                continue

        for service in Service.objects.all():
            if service.connection_check != 200:
                errors.append(
                    HealthCheckError(
                        code="improperly_configured_service",
                        message=_(
                            'Service "{service}" is improperly configured.'
                        ).format(service=service.label),
                        severity="error",
                    )
                )

        result = HealthCheckResult(check=self, errors=errors, success=len(errors) == 0)
        return result


class CatalogueHealthCheck(HealthCheck):
    def get_name(self) -> str:
        return _("Catalogue present")

    def run(self) -> HealthCheckResult:
        ztc_services = Service.objects.filter(api_type=APITypes.ztc)

        if not ztc_services.exists():
            return HealthCheckResult(
                check=self,
                success=False,
                errors=[
                    HealthCheckError(
                        code="no_ztc_error",
                        message=_("No ZTC services configured."),
                        severity="error",
                    )
                ],
            )

        errors = []

        catalogue_found = False
        for service in ztc_services:
            client = build_client(service)
            with client:
                response = None
                try:
                    response = client.get("catalogussen")
                except ConnectionError:
                    errors.append(
                        HealthCheckError(
                            code="connection_error",
                            message=_(
                                'Could not retrieve catalogues with service "{service}".'
                            ).format(service=service.label),
                            severity="error",
                            exc=traceback.format_exc(),
                        )
                    )
                    continue

                assert response is not None
                try:
                    response.raise_for_status()
                except HTTPError:
                    errors.append(
                        HealthCheckError(
                            code="response_error",
                            message=_(
                                'Received unexpected error response from catalogussen endpoint with service "{service}".'
                            ).format(service=service.label),
                            severity="error",
                            exc=traceback.format_exc(),
                        )
                    )
                    continue

                data = response.json()
                if data["count"] >= 1:
                    catalogue_found = True
                    break

                errors.append(
                    HealthCheckError(
                        code="no_catalogi_error",
                        message=_(
                            'No catalogues returned from catalogussen endpoint with service "{service}".'
                        ).format(service=service.label),
                        severity="warning",
                    )
                )

        if catalogue_found:
            return HealthCheckResult(
                check=self,
                success=True,
            )

        return HealthCheckResult(check=self, success=False, errors=errors)

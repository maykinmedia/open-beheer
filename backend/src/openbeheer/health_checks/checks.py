import traceback
from abc import ABC, abstractmethod
from typing import Union

from django.conf import settings
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _

from requests.exceptions import ConnectionError, HTTPError
from zgw_consumers.client import build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from .types import HealthCheckError, HealthCheckResult


class HealthCheck(ABC):
    human_name: Union[str, Promise]

    def __str__(self) -> str:
        return str(self.human_name) if self.human_name else self.__class__.__name__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__}: {self}>"

    @abstractmethod
    def run(self) -> HealthCheckResult: ...


class ServiceHealthCheck(HealthCheck):
    human_name = _("Services")

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
            service_connection_result = service.connection_check
            if service_connection_result is None or (
                service_connection_result and not 200 <= service_connection_result < 300
            ):
                errors.append(
                    HealthCheckError(
                        code="improperly_configured_service",
                        message=_(
                            'Service "{service}" is improperly configured.'
                        ).format(service=service.label),
                        severity="error",
                    )
                )

        result = HealthCheckResult(check=self, errors=errors)
        return result


class CatalogueHealthCheck(HealthCheck):
    human_name = _("Catalogue present")

    def run(self) -> HealthCheckResult:
        ztc_services = Service.objects.filter(api_type=APITypes.ztc)

        if not ztc_services.exists():
            return HealthCheckResult(
                check=self,
                errors=[
                    HealthCheckError(
                        code="no_ztc_error",
                        message=_("No ZTC services configured."),
                        severity="error",
                    )
                ],
            )

        errors = []
        for service in ztc_services:
            client = build_client(service)
            with client:
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

                try:
                    response.raise_for_status()
                except HTTPError:
                    errors.append(
                        HealthCheckError(
                            code="response_error",
                            message=_(
                                "Received unexpected error response from catalogussen "
                                'endpoint with service "{service}".'
                            ).format(service=service.label),
                            severity="error",
                            exc=traceback.format_exc(),
                        )
                    )
                    continue

                data = response.json()
                if data["count"] >= 1:
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

        return HealthCheckResult(check=self, errors=errors)

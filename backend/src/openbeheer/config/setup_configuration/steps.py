from django_setup_configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import ConfigurationRunFailed
from zgw_consumers.models import Service

from ..models import APIConfig
from .models import APIConfigConfigurationModel


class APIConfigConfigurationStep(BaseConfigurationStep[APIConfigConfigurationModel]):
    """Configure API settings"""

    config_model = APIConfigConfigurationModel
    enable_setting = "api_configuration_enabled"
    namespace = "api_configuration"
    verbose_name = "API Configuration"

    def execute(self, model: APIConfigConfigurationModel) -> None:
        config = APIConfig.get_solo()

        try:
            config.selectielijst_api_service = Service.objects.get(
                slug=model.selectielijst_service_identifier
            )
        except Service.DoesNotExist as exc:
            raise ConfigurationRunFailed(
                f"Could not find an existing `selectielijst` service with identifier `{model.selectielijst_service_identifier}`."
                " Make sure it is already configured, manually or by first running the configuration step of `zgw_consumers`."
            ) from exc

        try:
            config.objecttypen_api_service = Service.objects.get(
                slug=model.objecttypen_service_identifier
            )
        except Service.DoesNotExist as exc:
            raise ConfigurationRunFailed(
                f"Could not find an existing `objecttypen` service with identifier `{model.objecttypen_service_identifier}`."
                " Make sure it is already configured, manually or by first running the configuration step of `zgw_consumers`."
            ) from exc

        config.save(
            update_fields=["selectielijst_api_service", "objecttypen_api_service"]
        )

from django_setup_configuration import ConfigurationModel
from django_setup_configuration.fields import DjangoModelRef

from ..models import APIConfig


class APIConfigConfigurationModel(ConfigurationModel):
    selectielijst_service_identifier: str = DjangoModelRef(
        APIConfig, "selectielijst_api_service"
    )
    objecttypen_service_identifier: str = DjangoModelRef(
        APIConfig, "objecttypen_api_service"
    )

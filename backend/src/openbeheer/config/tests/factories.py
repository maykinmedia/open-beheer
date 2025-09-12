import factory
from factory.django import DjangoModelFactory
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from ..models import APIConfig


class APIConfigFactory(DjangoModelFactory[APIConfig]):
    selectielijst_api_service = factory.SubFactory(  # pyright: ignore[reportPrivateImportUsage]
        ServiceFactory,
        api_root="https://selectielijst.openzaak.nl/api/v1",
        api_type=APITypes.orc,
    )

    class Meta:  # type: ignore
        abstract = False
        model = APIConfig

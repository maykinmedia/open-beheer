import factory
from factory.django import DjangoModelFactory
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from ..models import APIConfig


class APIConfigFactory(DjangoModelFactory[APIConfig]):
    # Not mocking out the get_solo, as it would have hidden caching problems
    # Cache invalidation is hard, we shouldn't mock our way into a green CI.
    # note that this does come with test isolation issues.
    #
    # For the clients tests, this factory will remain the way to go; as it
    # exercises the real code. And we really want to test the real behaviour of
    # real code paths
    #
    # the rest, I don't expect to use any different values than the default
    # so it might not be a problem. Otherwise, running with pytest and have a
    # auto_use fixture that monkeypatches, is an option.

    selectielijst_api_service = factory.SubFactory(  # pyright: ignore[reportPrivateImportUsage]
        ServiceFactory,
        api_root="https://selectielijst.openzaak.nl/api/v1",
        api_type=APITypes.orc,
    )

    class Meta:  # type: ignore
        model = APIConfig

    @classmethod
    def _create(cls, model_class: type[APIConfig], *args, **kwargs):
        model_class.get_solo().delete()
        return super()._create(model_class, *args, **kwargs)

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CatalogiConfig(AppConfig):
    name = "openbeheer.catalogi"
    verbose_name = _("Catalogi")

    def ready(self):
        from .schema import MsgSpecStructExtension, GenericAliasExtension  # noqa

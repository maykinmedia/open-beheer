from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CatalogiConfig(AppConfig):
    name = "openbeheer.api"
    verbose_name = _("API")

    def ready(self):
        pass  # noqa

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ApiAppConfig(AppConfig):
    name = "openbeheer.api"
    verbose_name = _("API")

    def ready(self):
        from .drf_spectacular.schema import (
            MsgSpecFilterBackend,  # noqa: F401
            MsgSpecQueryParamsExtension,  # noqa: F401
        )

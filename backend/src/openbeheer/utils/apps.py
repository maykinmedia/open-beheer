from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "openbeheer.utils"

    def ready(self):
        from . import checks  # noqa

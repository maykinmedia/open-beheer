from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel


class APIConfig(SingletonModel):
    selectielijst_api_service = models.ForeignKey(
        to="zgw_consumers.Service",
        verbose_name=_("selectielijst API service"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Which service to use to query the Selectielijst API."),
    )

    class Meta:  # pyright:ignore[reportIncompatibleVariableOverride]
        verbose_name = _("API configuration")
        verbose_name_plural = _("API configurations")

    def __str__(self):
        return "API configuration"

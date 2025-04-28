from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from zgw_consumers.constants import APITypes
from django.utils.translation import gettext_lazy as _

from openbeheer.api.base.viewsets import ZGWViewSet


@extend_schema(
    tags=["Zaaktypen"],
    summary=_("Alle ZAAKTYPEn opvragen."),
    description=_("Deze lijst kan gefilterd wordt met query-string parameters."),
)
class ZaaktypenViewSet(ZGWViewSet):
    """
    Provides endpoints for ZTC Zaaktypen

    TODO: Response type (possibly from OAS?)
    """

    service_type = APITypes.ztc

    @action(methods=["GET"], detail=False)
    def zaaktypen(self, _) -> Response:
        return self.perform_list()

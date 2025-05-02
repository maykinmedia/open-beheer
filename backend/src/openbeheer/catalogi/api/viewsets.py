from drf_spectacular.utils import extend_schema
from zgw_consumers.constants import APITypes
from django.utils.translation import gettext_lazy as _

from openbeheer.api.base.viewsets import ZGWViewSet


@extend_schema(
    tags=["Zaaktypen"],
    summary=_("Alle ZAAKTYPEn opvragen."),
    description=_("Deze lijst kan gefilterd wordt met query-string parameters."),
)
class ZaaktypenViewSet(ZGWViewSet):
    service_type = APITypes.ztc


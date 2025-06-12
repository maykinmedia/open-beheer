from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema

from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from openbeheer.api.views import MsgspecAPIView

from openbeheer.types._open_beheer import OBOption


@extend_schema(
    tags=["Services"],
    summary=_("Get Open Zaak choices"),
    description=_(
        "Get the available Open Zaak catalogi instances. The value is the slug of the configured service, "
        "while the label is the name of the service."
    ),
    # responses={
    #     "200": list[OBOption[str]] # TODO blueprint of msgspec (Github #50)
    # }
)
class ServiceChoicesView(MsgspecAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        services = Service.objects.filter(api_type=APITypes.ztc)

        data = [
            OBOption(label=service.label, value=service.slug) for service in services
        ]
        return Response(data)

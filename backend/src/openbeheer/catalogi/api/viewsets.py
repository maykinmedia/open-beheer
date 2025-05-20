from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema

from git import TYPE_CHECKING
from zgw_consumers.constants import APITypes
from zgw_consumers.service import pagination_helper
from zgw_consumers.models import Service

from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from openbeheer.api.views import MsgspecAPIView
from openbeheer.clients import ztc_client

if TYPE_CHECKING:
    from openbeheer.types._open_beheer import OBOption



@extend_schema(
    summary=_("Get Open Zaak choices"),
    description=_(
        "Get the available Open Zaak catalogi instances. The value is the slug of the configured service, "
        "while the label is the name of the service."
    ),
    # responses={
    #     "200": list[OBOption[str]] # TODO blueprint of msgspec
    # }
)
class ServiceChoicesView(MsgspecAPIView): # TODO rebase on Chris PR
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        services = Service.objects.filter(api_type=APITypes.ztc)

        data = [{"label": service.label, "value": service.slug} for service in services]
        return Response(data)


@extend_schema(
    summary=_("Get catalogue choices"),
    description=_(
        "Retrieve the catalogues available in an Open Zaak instance. "
        "The value is the URL of the catalogus as returned from Open Zaak, "
        "while the label is the name of the catalogue (if configured) and otherwise the domain field."
    ),
    # responses={
    #     "200": list[OBOption[str]] # TODO blueprint of msgspec
    # }
)
class CatalogChoicesView(MsgspecAPIView): # TODO rebase on Chris PR
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str) -> Response:
        client = ztc_client(slug)

        response = client.get("/catalogussen")
        # TODO error handling on OZ unexpected response
        response.raise_for_status()

        results: list[OBOption[str]] = []
        for page in pagination_helper(
            client,
            response,
        ):
            # TODO validate response data with msgspec type
            results += [
                {
                    "label": f"{catalogue['naam']} ({catalogue['domein']})"
                    if catalogue.get("naam")
                    else catalogue["domein"],
                    "value": catalogue["url"],
                }
                for catalogue in page["results"]
            ]

        return Response(results)

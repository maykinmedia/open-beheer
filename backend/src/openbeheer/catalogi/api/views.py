from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema

from msgspec import convert
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from openbeheer.api.views import MsgspecAPIView
from openbeheer.clients import ztc_client, pagination_helper

from openbeheer.types.ztc import PaginatedCatalogusList

from openbeheer.types._open_beheer import OBOption


@extend_schema(
    tags=["Catalogi"],
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


@extend_schema(
    tags=["Catalogi"],
    summary=_("Get catalogue choices"),
    description=_(
        "Retrieve the catalogues available in an Open Zaak instance. "
        "The value is the URL of the catalogus as returned from Open Zaak, "
        "while the label is the name of the catalogue (if configured) and otherwise the domain field."
    ),
    # responses={
    #     "200": list[OBOption[str]] # TODO blueprint of msgspec (Github #50)
    # }
)
class CatalogChoicesView(MsgspecAPIView):
    def get(self, request: Request, slug: str) -> Response:
        # TODO for now, we only support one Open Zaak, so the slug
        # is not used.
        client = ztc_client()

        response = client.get("catalogussen")
        # TODO error handling on OZ unexpected response (Github #51)
        response.raise_for_status()

        results: list[OBOption[str]] = []
        for page_data in pagination_helper(
            client,
            response.json(),
        ):
            decoded_page_data = convert(
                page_data,
                type=PaginatedCatalogusList,
            )
            for catalogue in decoded_page_data.results:
                label = (
                    f"{catalogue.naam} ({catalogue.domein})"
                    if catalogue.naam
                    else catalogue.domein
                )
                # OZ API specs say that is is not required, but VNG specs say it is.
                # In practice, it is always present.
                value = catalogue.url.split("/")[-1]  # UUID.
                assert value

                results.append(OBOption(label=label, value=value))

        return Response(results)

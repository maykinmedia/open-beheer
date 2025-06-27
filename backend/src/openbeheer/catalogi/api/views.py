from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema, extend_schema_view

from msgspec import convert

from rest_framework.request import Request
from rest_framework.response import Response

from openbeheer.api.views import MsgspecAPIView
from openbeheer.clients import ztc_client, pagination_helper

from openbeheer.types.ztc import PaginatedCatalogusList

from openbeheer.types._open_beheer import ExternalServiceError, OBOption
from openbeheer.utils.decorators import handle_service_errors


@extend_schema_view(
    get=extend_schema(
        tags=["Catalogi"],
        summary=_("Get catalogue choices"),
        description=_(
            "Retrieve the catalogues available in an Open Zaak instance. "
            "The value is the URL of the catalogus as returned from Open Zaak, "
            "while the label is the name of the catalogue (if configured) and otherwise the domain field."
        ),
        responses={
            "200": list[OBOption[str]],
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    )
)
class CatalogChoicesView(MsgspecAPIView):
    @handle_service_errors
    def get(self, request: Request, slug: str) -> Response:
        client = ztc_client(slug)

        response = client.get("catalogussen")
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
                # OZ API specs say that url is not required, but VNG specs say it is.
                # In practice, it is always present.
                url = catalogue.url
                assert url
                path = f"{client.base_url}catalogussen/"
                uuid = url.removeprefix(path)
                assert uuid

                results.append(OBOption(label=label, value=uuid))

        return Response(results)

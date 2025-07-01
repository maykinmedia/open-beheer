from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from furl import furl
from drf_spectacular.utils import extend_schema, extend_schema_view
from msgspec.json import decode
from rest_framework.request import Request
from rest_framework.response import Response

from openbeheer.api.views import MsgspecAPIView
from openbeheer.clients import iter_pages, ztc_client
from openbeheer.types import ExternalServiceError, OBOption, as_ob_option
from openbeheer.types.ztc import Catalogus, PaginatedCatalogusList
from openbeheer.utils.decorators import handle_service_errors

if TYPE_CHECKING:
    from rest_framework.request import Request


# Shouldn't this have an inverse? Currently there is no way to go from
# the option.value back to the correct Catalogus; you'll always need the
# (option, client) pair.
@as_ob_option.register
def _as_option(catalogue: Catalogus, client) -> OBOption[str]:
    label = (
        f"{catalogue.naam} ({catalogue.domein})" if catalogue.naam else catalogue.domein
    )
    # OZ API specs say that url is not required, but VNG specs say it is.
    # In practice, it is always present.
    url = catalogue.url
    assert url
    path = f"{client.base_url}catalogussen/"
    uuid = url.removeprefix(path)
    assert uuid
    return OBOption(label=label, value=uuid)


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
        with ztc_client(slug) as client:
            response = client.get("catalogussen")
            response.raise_for_status()

            catalogues = decode(
                response.content,
                type=PaginatedCatalogusList,
            )
            results = [
                as_ob_option(catalogue, client)
                for catalogue in iter_pages(client, catalogues)
            ]

        return Response(results)

from uuid import UUID

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from openbeheer.api.views import (
    DetailView,
    DetailViewWithoutVersions,
    ListView,
    reverse,
)
from openbeheer.clients import ztc_client
from openbeheer.types import (
    BesluitTypeWithUUID,
    ExternalServiceError,
    ZGWError,
)
from openbeheer.types.ztc import (
    BesluitType,
    BesluitTypeRequest,
    PatchedBesluitTypeRequest,
)

from ..types import (
    BesluittypenGetParametersQuery,
)


@extend_schema_view(
    get=extend_schema(
        tags=["besluittypen"],
        summary="Get Besluittypen",
        parameters=[],
        filters=True,
        description="Retrive Besluittypen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["besluittypen"],
        summary="Create an Besluittypen",
        description="Create an Besluittypen.",
        request=BesluitTypeRequest,
        responses={
            "201": BesluitType,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class BesluittypeListView(
    ListView[
        BesluittypenGetParametersQuery,
        BesluitType,
        BesluitType,
    ]
):
    """
    Endpoint for Besluittypen attached to a particular Zaaktype.

    Beware, this is a many to many relationship. Other Zaaktypen may be attached
    to the same Besluittype.
    """

    data_type = BesluitType
    return_data_type = BesluitTypeWithUUID
    query_type = BesluittypenGetParametersQuery
    endpoint_path = "besluittypen"

    def post(
        self,
        request: Request,
        slug: str = "",
        zaaktype: UUID | None = None,
        **path_params,
    ) -> Response:
        # create besluittype
        response = super().post(request, slug, **path_params)
        as_url = reverse(slug)

        if zaaktype and status.is_success(response.status_code):
            # add it to the zaaktype
            with ztc_client(slug) as client:
                zaaktype_url = as_url("zaaktype", zaaktype)
                assert zaaktype_url
                get_response = client.get(zaaktype_url)
                if get_response.ok:
                    zaaktype_data = get_response.json()
                    patched = client.patch(
                        zaaktype_url,
                        json={
                            "besluittypen": zaaktype_data.get("besluittypen", [])
                            + [response.data.url]
                        },
                    )
                    if patched.ok:
                        response.data.zaaktypen.append(zaaktype_url)

        return response


@extend_schema_view(
    get=extend_schema(
        operation_id="service_besluittypen_retrieve_one",
        tags=["besluittypen"],
        summary="Get an Besluittype",
        description="Retrieve an Besluittype from Open Zaak.",
        responses={
            "200": BesluitType,
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["besluittypen"],
        summary="Patch an Besluittype",
        description="Partially update a Besluittype from Open Zaak.",
        request=PatchedBesluitTypeRequest,
        responses={
            "200": BesluitType,
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["besluittypen"],
        summary="Put an Besluittype",
        description="Fully update a Besluittype from Open Zaak.",
        request=BesluitTypeRequest,
        responses={
            "200": BesluitType,
            "400": ZGWError,
        },
    ),
    delete=extend_schema(
        tags=["besluittypen"],
        summary="Delete an Besluittype",
        description="Remove permanently a Besluittype from Open Zaak.",
        responses={
            "204": None,
            "400": ZGWError,
        },
    ),
)
class BesluittypeDetailView(DetailViewWithoutVersions, DetailView[BesluitType]):
    """
    Endpoint for Besluittypen attached to a particular Zaaktype
    """

    return_data_type = data_type = BesluitType
    endpoint_path = "besluittypen/{uuid}"
    expansions = {}

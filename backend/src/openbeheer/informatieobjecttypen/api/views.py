from collections.abc import Callable
from typing import Iterable, Mapping, override
from uuid import UUID

from ape_pie import APIClient
from drf_spectacular.utils import extend_schema, extend_schema_view
from msgspec.json import decode
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from openbeheer.api.views import (
    DetailView,
    DetailViewWithoutVersions,
    ListView,
    MsgspecAPIView,
)
from openbeheer.clients import ztc_client
from openbeheer.types import (
    DetailResponseWithoutVersions,
    ExternalServiceError,
    FrontendFieldsets,
    OBField,
    OBOption,
    ZGWError,
)
from openbeheer.types.ztc import (
    InformatieObjectType,
    InformatieObjectTypeRequest,
    PatchedInformatieObjectTypeRequest,
    VertrouwelijkheidaanduidingEnum,
)

from ..constants import INFORMATIEOBJECTTYPE_FIELDSETS
from ..types import (
    InformatieObjectTypenGetParametersQuery,
    InformatieObjectTypeSummary,
)


@extend_schema_view(
    get=extend_schema(
        tags=["Informatieobjecttypen"],
        summary="Get informatieobjecttypen",
        parameters=[],
        filters=True,
        description="Retrive informatieobjecttypen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["Informatieobjecttypen"],
        summary="Create an informatieobjecttypen",
        description="Create an informatieobjecttypen.",
        request=InformatieObjectTypeRequest,
        responses={
            "201": InformatieObjectType,  # TODO: Will probably change
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class InformatieObjectTypeListView(
    ListView[
        InformatieObjectTypenGetParametersQuery,
        InformatieObjectTypeSummary,
        InformatieObjectType,
    ]
):
    data_type = InformatieObjectType
    return_data_type = InformatieObjectTypeSummary
    query_type = InformatieObjectTypenGetParametersQuery
    endpoint_path = "informatieobjecttypen"

    @override
    def parse_ob_fields(
        self,
        params: InformatieObjectTypenGetParametersQuery,
        option_overrides: Mapping[str, list[OBOption]] = {},
        **_,
    ) -> list[OBField]:
        order = [
            "url",
            "omschrijving",
            "vertrouwelijkheidaanduiding",
            "versiedatum",
            "actief",
            "eindeGeldigheid",
            "concept",
        ]
        return super().parse_ob_fields(
            params,
            {
                "vertrouwelijkheidaanduiding": OBOption.from_enum(
                    VertrouwelijkheidaanduidingEnum
                )
            },
            sort_key=lambda f: order.index(f.name),
            base_editable=lambda _: False,  # no editable fields
        )

    def parse_query_params(self, request: Request, api_client: APIClient):
        params = super().parse_query_params(request, api_client)
        if params.catalogus:
            params.catalogus = f"{api_client.base_url}catalogussen/{params.catalogus}"

        if params.zaaktype:
            params.zaaktype = f"{api_client.base_url}zaaktypen/{params.zaaktype}"

        return params


@extend_schema_view(
    get=extend_schema(
        operation_id="service_informatieobjecttypen_retrieve_one",
        tags=["Informatieobjecttypen"],
        summary="Get an informatieobjecttype",
        description="Retrive an informatieobjecttype from Open Zaak.",
        responses={
            "200": DetailResponseWithoutVersions[InformatieObjectType],
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["Informatieobjecttypen"],
        summary="Patch an informatieobjecttype",
        description=(
            "Partially update a informatieobjecttype from Open Zaak. This will work only with "
            "an Open Zaak API token with the `catalogi.geforceerd-schrijven` permission if the informatieobjecttype is "
            "not a concept. Otherwise will return a 400."
        ),
        request=PatchedInformatieObjectTypeRequest,
        responses={
            "200": DetailResponseWithoutVersions[InformatieObjectType],
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["Informatieobjecttypen"],
        summary="Put an informatieobjecttype",
        description=(
            "Fully update an informatieobjecttype from Open Zaak. This will work only with "
            "an Open Zaak API token with the `catalogi.geforceerd-schrijven` permission if the informatieobjecttype is "
            "not a concept. Otherwise will return a 400."
        ),
        request=InformatieObjectTypeRequest,
        responses={
            "200": DetailResponseWithoutVersions[InformatieObjectType],
            "400": ZGWError,
        },
    ),
    delete=extend_schema(
        tags=["Informatieobjecttypen"],
        summary="Delete an informatieobjecttype",
        description=("Remove permanently an informatieobjecttype from OZ."),
        responses={
            "204": None,
            "400": ZGWError,
        },
    ),
)
class InformatieObjectTypeDetailView(
    DetailViewWithoutVersions, DetailView[InformatieObjectType]
):
    data_type = InformatieObjectType
    return_data_type = DetailResponseWithoutVersions[InformatieObjectType]
    endpoint_path = "informatieobjecttypen/{uuid}"

    expansions = {}

    def get_fieldsets(self) -> FrontendFieldsets:
        return INFORMATIEOBJECTTYPE_FIELDSETS

    def get_fields(
        self,
        data: InformatieObjectType,
        option_overrides: Mapping[str, list[OBOption]] = {},
        *,
        base_editable: Callable[[str], bool] = bool,
    ) -> Iterable[OBField]:
        # We can't to edit concept directly, we use the "publish" action to change it.
        yield from super().get_fields(
            data, option_overrides, base_editable=lambda name: name != "concept"
        )


class InformatieObjectTypePublishView(MsgspecAPIView):
    endpoint_path = "informatieobjecttypen/{uuid}/publish"

    @extend_schema(
        operation_id="informatieobjecttype_publish",
        summary="Publish an informatieobjecttype",
        tags=["Informatieobjecttypen"],
        responses={
            204: None,
            400: ZGWError,
        },
    )
    def post(self, request: Request, slug: str, uuid: UUID) -> Response:
        "Publish an informatieobjecttype"
        with ztc_client(slug) as client:
            response = client.post(
                self.endpoint_path.format(uuid=uuid),
            )

            if not response.ok:
                error = decode(response.content)
                return Response(
                    error,
                    status=response.status_code,
                )

        return Response(status=status.HTTP_204_NO_CONTENT)

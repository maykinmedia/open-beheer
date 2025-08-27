from typing import Mapping

from ape_pie import APIClient
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.request import Request

from openbeheer.api.views import DetailView, DetailViewWithoutVersions, ListView
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

    def parse_ob_fields(
        self,
        params: InformatieObjectTypenGetParametersQuery,
        option_overrides: Mapping[str, list[OBOption]] = {},
        **_,
    ) -> list[OBField]:
        return super().parse_ob_fields(
            params,
            {
                "vertrouwelijkheidaanduiding": OBOption.from_enum(
                    VertrouwelijkheidaanduidingEnum
                )
            },
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

    # TODO: not sure if we should expand the zaaktypen, since the IOT will be
    # shown under a specific zaaktype. But maybe all the other zaaktypen should be
    # expanded?
    expansions = {}

    def get_fieldsets(self) -> FrontendFieldsets:
        return INFORMATIEOBJECTTYPE_FIELDSETS

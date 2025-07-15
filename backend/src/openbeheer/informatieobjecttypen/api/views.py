from typing import Mapping

from ape_pie import APIClient
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.request import Request

from openbeheer.api.views import ListView
from openbeheer.informatieobjecttypen.types import (
    InformatieObjectTypenGetParametersQuery,
    InformatieObjectTypeSummary,
)
from openbeheer.types._open_beheer import (
    OBField,
    OBOption,
)
from openbeheer.types._zgw import ZGWError
from openbeheer.types.ztc import (
    InformatieObjectType,
    InformatieObjectTypeRequest,
    VertrouwelijkheidaanduidingEnum,
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
            "400": ZGWError,
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

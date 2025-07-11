from typing import Mapping
from openbeheer.api.views import ListView
from openbeheer.informatieobjecttypen.types import (
    InformatieObjectTypeSummary,
    InformatieObjectTypenGetParametersQuery,
)
from openbeheer.types._open_beheer import (
    ExternalServiceError,
    OBField,
    OBList,
    OBOption,
)
from openbeheer.types._zgw import ZGWError
from openbeheer.types.ztc import VertrouwelijkheidaanduidingEnum
from ape_pie import APIClient
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    get=extend_schema(
        tags=["Informatieobjecttypen"],
        summary="Get informatieobjecttypen",
        parameters=[],
        filters=True,
        description="Retrive informatieobjecttypen from Open Zaak.",
        responses={
            "200": OBList[InformatieObjectTypeSummary],
            "400": ZGWError,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class InformatieObjectTypeListView(
    ListView[InformatieObjectTypenGetParametersQuery, InformatieObjectTypeSummary]
):
    data_type = InformatieObjectTypeSummary
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

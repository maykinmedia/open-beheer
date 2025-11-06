from drf_spectacular.utils import extend_schema, extend_schema_view

from openbeheer.api.views import DetailView, DetailViewWithoutVersions, ListView
from openbeheer.types import (
    ExternalServiceError,
    ResultaatTypeWithUUID,
    ZGWError,
)
from openbeheer.types.ztc import (
    PatchedResultaatTypeRequest,
    ResultaatType,
    ResultaatTypeRequest,
)

from ..types import (
    ResultaatTypenGetParametersQuery,
)


@extend_schema_view(
    get=extend_schema(
        tags=["Resultaattypen"],
        summary="Get resultaattypen",
        parameters=[],
        filters=True,
        description="Retrive resultaattypen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["Resultaattypen"],
        summary="Create an resultaattypen",
        description="Create an resultaattypen.",
        request=ResultaatTypeRequest,
        responses={
            "201": ResultaatType,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class ResultaatTypeListView(
    ListView[
        ResultaatTypenGetParametersQuery,
        ResultaatType,
        ResultaatType,
    ]
):
    """
    Endpoint for Resultaattypen attached to a particular Zaaktype
    """

    data_type = ResultaatType
    return_data_type = ResultaatTypeWithUUID
    query_type = ResultaatTypenGetParametersQuery
    endpoint_path = "resultaattypen"


@extend_schema_view(
    get=extend_schema(
        operation_id="service_resultaattypen_retrieve_one",
        tags=["Resultaattypen"],
        summary="Get an resultaattype",
        description="Retrieve an resultaattype from Open Zaak.",
        responses={
            "200": ResultaatType,
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["Resultaattypen"],
        summary="Patch an resultaattype",
        description="Partially update a resultaattype from Open Zaak.",
        request=PatchedResultaatTypeRequest,
        responses={
            "200": ResultaatType,
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["Resultaattypen"],
        summary="Put an resultaattype",
        description="Fully update a resultaattype from Open Zaak.",
        request=ResultaatTypeRequest,
        responses={
            "200": ResultaatType,
            "400": ZGWError,
        },
    ),
    delete=extend_schema(
        tags=["Resultaattypen"],
        summary="Delete an resultaattype",
        description="Remove permanently a resultaattype from Open Zaak.",
        responses={
            "204": None,
            "400": ZGWError,
        },
    ),
)
class ResultaatTypeDetailView(DetailViewWithoutVersions, DetailView[ResultaatType]):
    """
    Endpoint for Resultaattypen attached to a particular Zaaktype
    """

    return_data_type = data_type = ResultaatTypeWithUUID
    endpoint_path = "resultaattypen/{uuid}"
    expansions = {}

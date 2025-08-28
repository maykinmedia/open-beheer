from drf_spectacular.utils import extend_schema, extend_schema_view

from openbeheer.api.views import DetailView, DetailViewWithoutVersions, ListView
from openbeheer.types import (
    ExternalServiceError,
    StatusTypeWithUUID,
    ZGWError,
)
from openbeheer.types.ztc import (
    PatchedStatusTypeRequest,
    StatusType,
    StatusTypeRequest,
)

from ..types import (
    StatustypenGetParametersQuery,
)


@extend_schema_view(
    get=extend_schema(
        tags=["statustypen"],
        summary="Get statustypen",
        parameters=[],
        filters=True,
        description="Retrive statustypen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["statustypen"],
        summary="Create an statustypen",
        description="Create an statustypen.",
        request=StatusTypeRequest,
        responses={
            "201": StatusType,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class StatusTypeListView(
    ListView[
        StatustypenGetParametersQuery,
        StatusType,
        StatusType,
    ]
):
    """
    Endpoint for statustypen attached to a particular Zaaktype
    """

    data_type = StatusType
    return_data_type = StatusTypeWithUUID
    query_type = StatustypenGetParametersQuery
    endpoint_path = "statustypen"


@extend_schema_view(
    get=extend_schema(
        operation_id="service_statustypen_retrieve_one",
        tags=["statustypen"],
        summary="Get an statustype",
        description="Retrieve an statustype from Open Zaak.",
        responses={
            "200": StatusType,
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["statustypen"],
        summary="Patch an statustype",
        description="Partially update a statustype from Open Zaak.",
        request=PatchedStatusTypeRequest,
        responses={
            "200": StatusType,
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["statustypen"],
        summary="Put an statustype",
        description="Fully update a statustype from Open Zaak.",
        request=StatusTypeRequest,
        responses={
            "200": StatusType,
            "400": ZGWError,
        },
    ),
    delete=extend_schema(
        tags=["statustypen"],
        summary="Delete an statustype",
        description="Remove permanently a statustype from Open Zaak.",
        responses={
            "204": None,
            "400": ZGWError,
        },
    ),
)
class StatusTypeDetailView(DetailViewWithoutVersions, DetailView[StatusType]):
    """
    Endpoint for statustypen attached to a particular Zaaktype
    """

    return_data_type = data_type = StatusType
    endpoint_path = "statustypen/{uuid}"
    expansions = {}

from drf_spectacular.utils import extend_schema, extend_schema_view

from openbeheer.api.views import DetailView, DetailViewWithoutVersions, ListView
from openbeheer.types import (
    EigenschapWithUUID,
    ExternalServiceError,
    ZGWError,
)
from openbeheer.types.ztc import (
    Eigenschap,
    EigenschapRequest,
    PatchedEigenschapRequest,
)

from ..types import (
    EigenschappenGetParametersQuery,
)


@extend_schema_view(
    get=extend_schema(
        tags=["eigenschappen"],
        summary="Get eigenschappen",
        parameters=[],
        filters=True,
        description="Retrieve eigenschappen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["eigenschappen"],
        summary="Create an eigenschappen",
        description="Create an eigenschappen.",
        request=EigenschapRequest,
        responses={
            "201": Eigenschap,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class EigenschappenListView(
    ListView[
        EigenschappenGetParametersQuery,
        Eigenschap,
        Eigenschap,
    ]
):
    """
    Endpoint for eigenschappen attached to a particular Zaaktype
    """

    data_type = Eigenschap
    return_data_type = EigenschapWithUUID
    query_type = EigenschappenGetParametersQuery
    endpoint_path = "eigenschappen"


@extend_schema_view(
    get=extend_schema(
        operation_id="service_eigenschappen_retrieve_one",
        tags=["eigenschappen"],
        summary="Get an eigenschappe",
        description="Retrieve an eigenschappe from Open Zaak.",
        responses={
            "200": Eigenschap,
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["eigenschappen"],
        summary="Patch an eigenschappe",
        description="Partially update a eigenschappe from Open Zaak.",
        request=PatchedEigenschapRequest,
        responses={
            "200": Eigenschap,
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["eigenschappen"],
        summary="Put an eigenschappe",
        description="Fully update a eigenschappe from Open Zaak.",
        request=EigenschapRequest,
        responses={
            "200": Eigenschap,
            "400": ZGWError,
        },
    ),
    delete=extend_schema(
        tags=["eigenschappen"],
        summary="Delete an eigenschappe",
        description="Remove permanently a eigenschappe from Open Zaak.",
        responses={
            "204": None,
            "400": ZGWError,
        },
    ),
)
class EigenschappenDetailView(DetailViewWithoutVersions, DetailView[Eigenschap]):
    """
    Endpoint for eigenschappen attached to a particular Zaaktype
    """

    return_data_type = data_type = Eigenschap
    endpoint_path = "eigenschappen/{uuid}"
    expansions = {}

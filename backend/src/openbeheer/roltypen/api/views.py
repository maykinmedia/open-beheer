from drf_spectacular.utils import extend_schema, extend_schema_view

from openbeheer.api.views import DetailView, DetailViewWithoutVersions, ListView
from openbeheer.types import (
    ExternalServiceError,
    RolTypeWithUUID,
)
from openbeheer.types.ztc import (
    PatchedRolTypeRequest,
    RolType,
    RolTypeRequest,
)

from ..types import (
    RoltypenGetParametersQuery,
)


@extend_schema_view(
    get=extend_schema(
        tags=["roltypen"],
        summary="Get roltypen",
        parameters=[],
        filters=True,
        description="Retrive roltypen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["roltypen"],
        summary="Create an roltypen",
        description="Create an roltypen.",
        request=RolTypeRequest,
        responses={
            "201": RolType,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class RoltypeListView(
    ListView[
        RoltypenGetParametersQuery,
        RolTypeWithUUID,
        RolType,
    ]
):
    """
    Endpoint for roltypen attached to a particular Zaaktype
    """

    data_type = RolType
    return_data_type = RolTypeWithUUID
    query_type = RoltypenGetParametersQuery
    endpoint_path = "roltypen"


@extend_schema_view(
    get=extend_schema(
        operation_id="service_roltypen_retrieve_one",
        tags=["roltypen"],
        summary="Get an roltype",
        description="Retrieve an roltype from Open Zaak.",
    ),
    patch=extend_schema(
        tags=["roltypen"],
        summary="Patch an roltype",
        description="Partially update a roltype from Open Zaak.",
        request=PatchedRolTypeRequest,
    ),
    put=extend_schema(
        tags=["roltypen"],
        summary="Put an roltype",
        description="Fully update a roltype from Open Zaak.",
        request=RolTypeRequest,
    ),
    delete=extend_schema(
        tags=["roltypen"],
        summary="Delete an roltype",
        description="Remove permanently a roltype from Open Zaak.",
    ),
)
class RoltypeDetailView(DetailViewWithoutVersions, DetailView[RolType]):
    """
    Endpoint for roltypen attached to a particular Zaaktype
    """

    return_data_type = data_type = RolTypeWithUUID
    endpoint_path = "roltypen/{uuid}"
    expansions = {}

from drf_spectacular.utils import extend_schema, extend_schema_view

from openbeheer.api.views import DetailView, DetailViewWithoutVersions, ListView
from openbeheer.types import (
    ExternalServiceError,
    ZaakObjectTypeWithUUID,
    ZGWError,
)
from openbeheer.types.ztc import (
    PatchedZaakObjectTypeRequest,
    ZaakObjectType,
    ZaakObjectTypeRequest,
)

from ..types import (
    ZaakobjecttypenGetParametersQuery,
)


@extend_schema_view(
    get=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Get zaakobjecttypen",
        parameters=[],
        filters=True,
        description="Retrive zaakobjecttypen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Create an zaakobjecttypen",
        description="Create an zaakobjecttypen.",
        request=ZaakObjectTypeRequest,
        responses={
            "201": ZaakObjectType,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class ZaakObjectTypeListView(
    ListView[
        ZaakobjecttypenGetParametersQuery,
        ZaakObjectType,
        ZaakObjectType,
    ]
):
    """
    Endpoint for zaakobjecttypen attached to a particular Zaaktype
    """

    data_type = ZaakObjectType
    return_data_type = ZaakObjectTypeWithUUID
    query_type = ZaakobjecttypenGetParametersQuery
    endpoint_path = "zaakobjecttypen"


@extend_schema_view(
    get=extend_schema(
        operation_id="service_zaakobjecttypen_retrieve_one",
        tags=["zaakobjecttypen"],
        summary="Get an zaakobjecttype",
        description="Retrieve an zaakobjecttype from Open Zaak.",
        responses={
            "200": ZaakObjectType,
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Patch an zaakobjecttype",
        description="Partially update a zaakobjecttype from Open Zaak.",
        request=PatchedZaakObjectTypeRequest,
        responses={
            "200": ZaakObjectType,
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Put an zaakobjecttype",
        description="Fully update a zaakobjecttype from Open Zaak.",
        request=ZaakObjectTypeRequest,
        responses={
            "200": ZaakObjectType,
            "400": ZGWError,
        },
    ),
    delete=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Delete an zaakobjecttype",
        description="Remove permanently a zaakobjecttype from Open Zaak.",
        responses={
            "204": None,
            "400": ZGWError,
        },
    ),
)
class ZaakObjectTypeDetailView(DetailViewWithoutVersions, DetailView[ZaakObjectType]):
    """
    Endpoint for zaakobjecttypen attached to a particular Zaaktype
    """

    return_data_type = data_type = ZaakObjectType
    endpoint_path = "zaakobjecttypen/{uuid}"
    expansions = {}

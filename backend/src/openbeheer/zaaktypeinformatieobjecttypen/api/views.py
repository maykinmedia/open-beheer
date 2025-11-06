from drf_spectacular.utils import extend_schema, extend_schema_view

from openbeheer.api.views import (
    DetailView,
    DetailViewWithoutVersions,
    ListView,
)
from openbeheer.types import (
    ExternalServiceError,
    ZGWError,
)
from openbeheer.types._open_beheer import ZaakTypeInformatieObjectTypeWithUUID
from openbeheer.types.ztc import (
    PatchedZaakTypeInformatieObjectTypeRequest,
    ZaakTypeInformatieObjectType,
    ZaakTypeInformatieObjectTypeRequest,
)
from openbeheer.zaaktypeinformatieobjecttypen.types import (
    ZaaktypeInformatieobjecttypenGetParametersQuery,
)


@extend_schema_view(
    get=extend_schema(
        tags=["Zaaktype-Informatieobjecttypen"],
        summary="Get zaaktype-informatieobjecttypen",
        parameters=[],
        filters=True,
        description="Retrive zaaktype-informatieobjecttypen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["Zaaktype-Informatieobjecttypen"],
        summary="Create a zaaktype-informatieobjecttype",
        description=(
            "Create a zaaktype-informatieobjecttype. "
            "The informatieobjecttype and the zaaktype need to belong to the same catalogus"
        ),
        request=ZaakTypeInformatieObjectTypeRequest,
        responses={
            "201": ZaakTypeInformatieObjectType,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class ZaakTypeInformatieobjecttypeListView(
    ListView[
        ZaaktypeInformatieobjecttypenGetParametersQuery,
        ZaakTypeInformatieObjectType,
        ZaakTypeInformatieObjectType,
    ]
):
    """
    Endpoint for zaaktypeinformatieobjecttypen attached to a particular Zaaktype
    """

    data_type = ZaakTypeInformatieObjectType
    return_data_type = ZaakTypeInformatieObjectTypeWithUUID
    query_type = ZaaktypeInformatieobjecttypenGetParametersQuery
    endpoint_path = "zaaktype-informatieobjecttypen"


@extend_schema_view(
    get=extend_schema(
        operation_id="service_zaaktypeinformatieobjecttypen_retrieve_one",
        tags=["Zaaktype-Informatieobjecttypen"],
        summary="Get an zaaktype_informatieobjecttype",
        description="Retrieve an zaaktype_informatieobjecttype from Open Zaak.",
        responses={
            "200": ZaakTypeInformatieObjectType,
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["Zaaktype-Informatieobjecttypen"],
        summary="Patch an zaaktype_informatieobjecttype",
        description="Partially update a zaaktype_informatieobjecttype from Open Zaak.",
        request=PatchedZaakTypeInformatieObjectTypeRequest,
        responses={
            "200": ZaakTypeInformatieObjectType,
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["Zaaktype-Informatieobjecttypen"],
        summary="Put an zaaktype_informatieobjecttype",
        description="Fully update a zaaktype_informatieobjecttype from Open Zaak.",
        request=ZaakTypeInformatieObjectTypeRequest,
        responses={
            "200": ZaakTypeInformatieObjectType,
            "400": ZGWError,
        },
    ),
    delete=extend_schema(
        tags=["Zaaktype-Informatieobjecttypen"],
        summary="Delete an zaaktype_informatieobjecttype",
        description="Remove permanently a zaaktype_informatieobjecttype from Open Zaak.",
        responses={
            "204": None,
            "400": ZGWError,
        },
    ),
)
class ZaakTypeInformatieObjectTypeDetailView(
    DetailViewWithoutVersions, DetailView[ZaakTypeInformatieObjectType]
):
    """
    Endpoint for zaaktypeinformatieobjecttypen attached to a particular Zaaktype
    """

    return_data_type = data_type = ZaakTypeInformatieObjectTypeWithUUID
    endpoint_path = "zaaktype-informatieobjecttypen/{uuid}"

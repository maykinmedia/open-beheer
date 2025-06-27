import datetime
from typing import Annotated, Mapping
from ape_pie import APIClient
from msgspec import UNSET, Meta, Struct, UnsetType
from rest_framework.request import Request
from msgspec.json import decode
from msgspec import convert
from openbeheer.api.views import ListView
from openbeheer.types._zgw import ZGWError, ZGWResponse
from openbeheer.types.ztc import (
    PatchedZaakTypeRequest,
    Status,
    VertrouwelijkheidaanduidingEnum,
    ZaakTypeRequest,
)
from openbeheer.types._open_beheer import ExternalServiceError
from openbeheer.types import OBPagedQueryParams, OBField, OBOption
from drf_spectacular.utils import extend_schema, extend_schema_view
from openbeheer.api.views import DetailView
from openbeheer.clients import pagination_helper, ztc_client
from openbeheer.types._open_beheer import (
    DetailResponse,
    FrontendFieldsets,
    VersionSummary,
)
from openbeheer.types.ztc import (
    PaginatedZaakTypeList,
    ZaakType,
)
from furl import furl
from openbeheer.zaaktype.constants import ZAAKTYPE_FIELDSETS


class ZaaktypenGetParametersQuery(OBPagedQueryParams, kw_only=True, rename="camel"):
    catalogus: Annotated[
        str | UnsetType, Meta(description="UUID part of the catalogus URL")
    ] = UNSET  # frontend uuid.UUID, backend url
    datum_geldigheid: datetime.date | UnsetType = UNSET
    identificatie: str | UnsetType = UNSET
    page: int = 1
    status: Status = Status.alles  # OZ defaults to definitief
    trefwoorden: Annotated[
        str | UnsetType, Meta(description="Comma separated keywords")
    ] = UNSET


class ZaakTypeSummary(Struct, kw_only=True, rename="camel"):
    # Identificate
    # Omschrijving
    # Actief ja/nee
    # Einddatum
    # Omschrijving
    # Vertrouwelijkheidaanduiding

    url: str
    identificatie: str
    omschrijving: str
    # Actief ja/nee: calculated
    actief: bool | UnsetType = UNSET
    einde_geldigheid: datetime.date | None = None
    # str, because VertrouwelijkheidaanduidingEnum does not contain "" but OZ does
    # XXX: the "" is actually a fault in the fixtures!
    vertrouwelijkheidaanduiding: str
    versiedatum: datetime.date

    def __post_init__(self):
        self.actief = (
            self.einde_geldigheid is None
            or datetime.date.today() < self.einde_geldigheid
        )


@extend_schema_view(
    get=extend_schema(
        tags=["Zaaktypen"],
        summary="Get zaaktypen",
        parameters=[],
        filters=True,
        description="Retrive zaaktypen from Open Zaak.",
        responses={
            "200": ZGWResponse[ZaakTypeSummary],
            "400": ZGWError,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    )
)
class ZaakTypeListView(ListView[ZaaktypenGetParametersQuery, ZaakTypeSummary]):
    data_type = ZaakTypeSummary
    query_type = ZaaktypenGetParametersQuery
    endpoint_path = "zaaktypen"

    def parse_ob_fields(
        self,
        params: ZaaktypenGetParametersQuery,
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
        return params


@extend_schema_view(
    get=extend_schema(
        tags=["Zaaktypen"],
        summary="Get a zaaktype",
        description="Retrive a zaaktype from Open Zaak.",
        responses={
            "200": DetailResponse[ZaakType],
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["Zaaktypen"],
        summary="Patch a zaaktype",
        description=(
            "Partially update a zaaktype from Open Zaak. According to OZ specs, this should only work with"
            " draft zaaktypen. In practice, it modifies also the non-draft zaaktypen."
        ),
        request=PatchedZaakTypeRequest,
        responses={
            "200": DetailResponse[ZaakType],
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["Zaaktypen"],
        summary="Put a zaaktype",
        description=(
            "Fully update a zaaktype from Open Zaak. According to OZ specs, this should only work with"
            " draft zaaktypen. In practice, it modifies also the non-draft zaaktypen."
        ),
        request=ZaakTypeRequest,
        responses={
            "200": DetailResponse[ZaakType],
            "400": ZGWError,
        },
    ),
)
class ZaakTypeDetailView(DetailView[ZaakType]):
    data_type = ZaakType
    endpoint_path = "zaaktypen/{uuid}"
    has_versions = True

    def get_item_versions(
        self, slug: str, data: ZaakType
    ) -> tuple[list[ZaakType] | ZGWError, int]:
        # TODO: Question: should we keep the versions "paginated"? (I don't think so)
        with ztc_client() as client:
            response = client.get(
                "zaaktypen",
                params={"identificatie": data.identificatie},
            )

        if not response.ok:
            error = decode(response.content, type=ZGWError)
            return error, response.status_code

        results: list[ZaakType] = []
        for page_data in pagination_helper(
            client,
            response.json(),
        ):
            decoded_page_data = convert(
                page_data,
                type=PaginatedZaakTypeList,
            )
            results.extend(decoded_page_data.results)

        return results, response.status_code

    def format_version(self, data: ZaakType) -> VersionSummary:
        assert (
            data.url
        )  # The specs say that it is optional, but in practice it's always present
        zaaktype_url = furl(data.url)
        uuid = zaaktype_url.path.segments[-1]

        return VersionSummary(
            uuid=uuid,
            begin_geldigheid=data.begin_geldigheid,
            einde_geldigheid=data.einde_geldigheid,
            concept=data.concept,
        )

    def get_fieldsets(self) -> FrontendFieldsets:
        return ZAAKTYPE_FIELDSETS

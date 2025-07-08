from collections.abc import Iterable
import datetime
from typing import Annotated, Mapping

from ape_pie import APIClient
from drf_spectacular.utils import extend_schema, extend_schema_view
from furl import furl
from msgspec import UNSET, Meta, Struct, UnsetType, field
from msgspec.json import decode
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from openbeheer.api.views import (
    DetailView,
    ListView,
    fetch_one,
    make_expandable,
    make_expansion,
)
from openbeheer.clients import iter_pages, ztc_client
from openbeheer.types import OBField, OBOption, OBPagedQueryParams
from openbeheer.types._open_beheer import (
    DetailResponse,
    ExternalServiceError,
    FrontendFieldsets,
    VersionSummary,
)
from openbeheer.types._zgw import ZGWError, ZGWResponse
from openbeheer.types.ztc import (
    BesluitType,
    Eigenschap,
    InformatieObjectType,
    PaginatedZaakTypeList,
    PatchedZaakTypeRequest,
    ResultaatType,
    RolType,
    Status,
    StatusType,
    VertrouwelijkheidaanduidingEnum,
    ZaakObjectType,
    ZaakType,
    ZaakTypeRequest,
)
from openbeheer.utils.decorators import handle_service_errors
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


class ZaakTypeSummary(Struct, kw_only=True):
    url: str
    identificatie: str
    omschrijving: str
    # Actief ja/nee: calculated
    actief: bool | UnsetType = UNSET
    einde_geldigheid: datetime.date | None = field(default=None, name="eindeGeldigheid")
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
    ),
    post=extend_schema(
        tags=["Zaaktypen"],
        summary="Create a zaaktype",
        description="Create a zaaktype.",
        request=ZaakTypeRequest,
        responses={
            "201": ZaakType,
            "400": ZGWError,
        },
    ),
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

    @handle_service_errors
    def post(self, request: Request, slug: str = "") -> Response:
        with ztc_client(slug) as client:
            response = client.post(self.endpoint_path, json=request.data)

        if not response.ok:
            error = decode(response.content, type=ZGWError)
            return Response(
                error,
                status=response.status_code,
            )

        data = decode(
            response.content,
            type=ZaakType,
            strict=False,
        )

        return Response(data, status.HTTP_201_CREATED)


ExpandableZaakType = make_expandable(
    ZaakType,
    {
        "besluittypen": list[BesluitType],
        # Not invented here:
        # "selectielijst_procestype": "https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0",
        # Posssibly Not invented here:
        # "gerelateerde_zaaktypen": null,
        # "broncatalogus.url": null,
        # "bronzaaktype.url": null,
        "statustypen": list[StatusType],
        "resultaattypen": list[ResultaatType],
        "eigenschappen": list[Eigenschap],
        "informatieobjecttypen": list[InformatieObjectType],
        "roltypen": list[RolType],
        "deelzaaktypen": list[ZaakType],
        "zaakobjecttypen": list[ZaakObjectType],
    },
)


def expand_deelzaaktype(
    client: APIClient, zaaktypen: Iterable[ZaakType]
) -> list[list[ZaakType | None]]:
    return [
        [
            fetch_one(client, dz_url, ZaakType) if dz_url else None
            for dz_url in (zt.deelzaaktypen or [])
        ]
        for zt in zaaktypen
    ]


@extend_schema_view(
    get=extend_schema(
        tags=["Zaaktypen"],
        summary="Get a zaaktype",
        description="Retrive a zaaktype from Open Zaak.",
        responses={
            "200": DetailResponse[ExpandableZaakType],
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
            "200": DetailResponse[ExpandableZaakType],
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
            "200": DetailResponse[ExpandableZaakType],
            "400": ZGWError,
        },
    ),
)
class ZaakTypeDetailView(DetailView[ExpandableZaakType]):
    data_type = ExpandableZaakType
    endpoint_path = "zaaktypen/{uuid}"
    has_versions = True

    @staticmethod
    def _get_params_with_status(zaaktype: ZaakType):
        return {"zaaktype": zaaktype.url, "status": "alles"}

    @staticmethod
    def _key(zaaktype: ZaakType):
        return {"zaaktype": zaaktype.url}

    expansions = {
        "besluittypen": make_expansion(
            "besluittypen",
            # "zaaktypen" is probably a typo in the VNG spec, it doesn't look like
            # it actually accepts multiple so we can't use a __in
            lambda zt: {"zaaktypen": zt.url, "status": "alles"},  # pyright: ignore[reportAttributeAccessIssue]
            BesluitType,
        ),
        "statustypen": make_expansion(
            "statustypen", _get_params_with_status, StatusType
        ),
        # TODO investigate bad OZ response
        "resultaattypen": make_expansion(
            "resultaattypen", _get_params_with_status, dict
        ),
        "eigenschappen": make_expansion(
            "eigenschappen", _get_params_with_status, Eigenschap
        ),
        "informatieobjecttypen": make_expansion(
            "informatieobjecttypen", _get_params_with_status, InformatieObjectType
        ),
        "roltypen": make_expansion("roltypen", _get_params_with_status, RolType),
        "deelzaaktypen": expand_deelzaaktype,
        "zaakobjecttypen": make_expansion("zaakobjecttypen", _key, ZaakObjectType),
    }

    def get_item_versions(
        self, slug: str, data: ZaakType
    ) -> tuple[list[ZaakType] | ZGWError, int]:
        # TODO: Question: should we keep the versions "paginated"? (I don't think so)
        with ztc_client() as client:
            response = client.get(
                "zaaktypen",
                params={"identificatie": data.identificatie, "status": "alles"},
            )

        if not response.ok:
            error = decode(response.content, type=ZGWError)
            return error, response.status_code

        zaaktypen = decode(response.content, type=PaginatedZaakTypeList)

        results = list(iter_pages(client, zaaktypen))

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

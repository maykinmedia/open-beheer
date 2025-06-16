import datetime
from typing import Mapping

from ape_pie import APIClient
from msgspec import UNSET, Struct, UnsetType
from rest_framework.request import Request
from openbeheer.api.views import ListView
from openbeheer.types._zgw import ZGWResponse
from openbeheer.types.ztc import Status, ValidatieFout, VertrouwelijkheidaanduidingEnum
from openbeheer.types import OBPagedQueryParams, OBField, OBOption
from drf_spectacular.utils import extend_schema, extend_schema_view


class ZaaktypenGetParametersQuery(OBPagedQueryParams, kw_only=True, rename="camel"):
    catalogus: str | UnsetType = UNSET  # frontend uuid.UUID, backend url
    datum_geldigheid: str | UnsetType = UNSET
    identificatie: str | UnsetType = UNSET
    page: int = 1
    status: Status = Status.alles  # OZ defaults to definitief
    trefwoorden: str | UnsetType = UNSET


class ZaakType(Struct, kw_only=True, rename="camel"):
    # Identificate
    # Omschrijving
    # Actief ja/nee
    # Einddatum
    # Omschrijving
    # Vertrouwelijkheidaanduiding

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
            "200": ZGWResponse[ZaakType],
            "400": ValidatieFout,
        },
    )
)
class ZaakTypeListView(ListView[ZaaktypenGetParametersQuery, ZaakType]):
    data_type = ZaakType
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

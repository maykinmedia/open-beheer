import datetime
from typing import Mapping

from msgspec import UNSET, Struct, UnsetType, field
from openbeheer.api.views import ListView
from openbeheer.types._zgw import ZGWResponse
from openbeheer.types.ztc import Status, ValidatieFout, VertrouwelijkheidaanduidingEnum
from openbeheer.types import OBPagedQueryParams, OBField, OBOption
from drf_spectacular.utils import extend_schema, extend_schema_view


class ZaaktypenGetParametersQuery(OBPagedQueryParams, kw_only=True):
    catalogus: int | None = None
    datum_geldigheid: str | None = field(name="datumGeldigheid", default=None)
    identificatie: str | None = None
    page: int = 1
    status: Status | None = None
    trefwoorden: list[str] = []


class ZaakType(Struct, kw_only=True):
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
        description="Retrive zaaktypen from Open Zaak.",
        responses={
            "200": ZGWResponse[ZaakType],
            "400": ValidatieFout,
        },
    )
)
class ZaakTypeListView(ListView):
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

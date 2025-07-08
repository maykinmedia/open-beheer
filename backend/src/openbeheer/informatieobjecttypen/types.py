import datetime
from typing import Annotated

from msgspec import UNSET, Meta, UnsetType

from openbeheer.types._open_beheer import OBPagedQueryParams, VersionedResourceSummary
from openbeheer.types.ztc import Status


class InformatieObjectTypenGetParametersQuery(
    OBPagedQueryParams, kw_only=True, rename="camel"
):
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
    zaaktype: Annotated[
        str | UnsetType, Meta(description="UUID part of the zaaktype URL.")
    ] = UNSET


class InformatieObjectTypeSummary(
    VersionedResourceSummary, kw_only=True, rename="camel"
):
    url: str
    omschrijving: str
    # str, because VertrouwelijkheidaanduidingEnum does not contain "" but OZ does
    vertrouwelijkheidaanduiding: str
    # Actief true/false: calculated for ja/nee in the frontend
    actief: bool | UnsetType = UNSET
    einde_geldigheid: datetime.date | None = None
    concept: bool | UnsetType = UNSET

import datetime
from typing import Annotated

from msgspec import UNSET, Meta, UnsetType

from openbeheer.types import OBPagedQueryParams


class ZaakobjecttypenGetParametersQuery(
    OBPagedQueryParams, kw_only=True, rename="camel"
):
    ander_objecttype: bool | UnsetType = UNSET
    catalogus: Annotated[
        str | UnsetType, Meta(description="UUID part of the catalogus URL.")
    ] = UNSET
    datum_begin_geldigheid: datetime.date | UnsetType = UNSET
    datum_einde_geldigheid: datetime.date | UnsetType = UNSET
    datum_geldigheid: datetime.date | UnsetType = UNSET
    objecttype: str | None = None
    relatie_omschrijving: str | UnsetType = UNSET
    zaaktype: Annotated[
        str | UnsetType, Meta(description="UUID part of the zaaktype URL.")
    ] = UNSET
    zaaktype_identificatie: str | UnsetType = UNSET

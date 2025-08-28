import datetime
from typing import Annotated

from msgspec import UNSET, Meta, UnsetType

from openbeheer.types import OBPagedQueryParams
from openbeheer.types.ztc import Status


class BesluittypenGetParametersQuery(OBPagedQueryParams, kw_only=True, rename="camel"):
    datum_geldigheid: datetime.date | UnsetType = UNSET
    informatieobjecttypen: str | None = None
    omschrijving: str | None = None
    status: Status = Status.alles  # OZ defaults to definitief
    zaaktypen: Annotated[
        str | UnsetType, Meta(description="UUID part of the zaaktype URL.")
    ] = UNSET

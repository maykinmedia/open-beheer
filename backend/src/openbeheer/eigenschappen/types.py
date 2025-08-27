import datetime
from typing import Annotated

from msgspec import UNSET, Meta, UnsetType

from openbeheer.types import OBPagedQueryParams
from openbeheer.types.ztc import Status


class EigenschappenGetParametersQuery(OBPagedQueryParams, kw_only=True, rename="camel"):
    # Can't be filterd on catalog, so a /eigenschappen endpoint at the root
    # would be a problem
    datum_geldigheid: datetime.date | UnsetType = UNSET
    status: Status = Status.alles  # OZ defaults to definitief
    zaaktype: Annotated[
        str | UnsetType, Meta(description="UUID part of the zaaktype URL.")
    ] = UNSET
    zaaktype_identificatie: str | UnsetType = UNSET

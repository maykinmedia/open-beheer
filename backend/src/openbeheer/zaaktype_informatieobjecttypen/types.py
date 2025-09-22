from typing import Annotated

from msgspec import UNSET, Meta, UnsetType

from openbeheer.types import OBPagedQueryParams
from openbeheer.types.ztc import Richting, Status


class ZaaktypeInformatieobjecttypenGetParametersQuery(
    OBPagedQueryParams, kw_only=True, rename="camel"
):
    informatieobjecttype: Annotated[
        str | UnsetType, Meta(description="UUID part of the informatieobjecttype URL.")
    ] = UNSET

    richting: Richting | None = None
    status: Status = Status.alles  # OZ defaults to definitief
    zaaktype: Annotated[
        str | UnsetType, Meta(description="UUID part of the zaaktype URL.")
    ] = UNSET

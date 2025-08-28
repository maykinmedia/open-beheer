import datetime
from typing import Annotated

from msgspec import UNSET, Meta, Struct, UnsetType

from openbeheer.types import OBPagedQueryParams
from openbeheer.types.ztc import OmschrijvingGeneriek4, Status


class RoltypenGetParametersQuery(OBPagedQueryParams, kw_only=True, rename="camel"):
    # Can't be filterd on catalog, so a /roltypen endpoint at the root
    # would be a problem
    datum_geldigheid: datetime.date | UnsetType = UNSET
    status: Status = Status.alles  # OZ defaults to definitief
    zaaktype: Annotated[
        str | UnsetType, Meta(description="UUID part of the zaaktype URL.")
    ] = UNSET
    zaaktype_identificatie: str | UnsetType = UNSET

    omschrijving: str | None = None
    omschrijving_generiek: OmschrijvingGeneriek4 | UnsetType = UNSET


class RoltypeSummary(Struct, kw_only=True, rename="camel"):
    url: str
    omschrijving: str
    begin_geldigheid: datetime.date | None = None
    einde_geldigheid: datetime.date | None = None

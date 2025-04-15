"""Zaak Registratie Component DTO's

These are the types of the responses of the ZRC API.
"""

import datetime
import uuid

from msgspec import Struct

from ._sundry import URL
from ._ztc import Statustype, Zaaktype


class StatusExpansion(Struct, frozen=True):
    statustype: Statustype | None = None


class Status(Struct, rename="camel"):
    "ZRC.STATUS van een ZRC.ZAAK"

    url: URL
    datum_status_gezet: datetime.datetime
    statustype: URL
    statustoelichting: str
    _expand: StatusExpansion = StatusExpansion()


class ZaakExpansion(Struct, frozen=True):
    """
    Expanded attributes of a ZRC.ZAAK

    Some attributes are urls of other objects. The `expand` request
    parameter puts these whole objects in an _expand object on the
    response, so no extra requests are needed"
    Which attributes are not `None` depends on the request.
    """

    status: Status | None = None
    zaaktype: Zaaktype | None = None


class Zaak(Struct, rename="camel"):
    "ZRC.ZAAK"

    url: URL
    uuid: uuid.UUID
    identificatie: str
    zaaktype: URL
    bronorganisatie: str
    toelichting: str
    registratiedatum: datetime.date
    startdatum: datetime.date
    verantwoordelijke_organisatie: str
    _expand: ZaakExpansion = ZaakExpansion()
    omschrijving: str | None = None
    einddatum: datetime.date | None = None

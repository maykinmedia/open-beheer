"""Data Transfer Object types for both ZGW APIs facing side, and our frontend."""

from ._open_beheer import (
    OBField,
    OBFieldType,
    OBList,
    OBPagination,
    as_ob_option,
)
from ._sundry import URL
from ._zgw import ZGWError, ZGWResponse
from ._zrc import Zaak
from ._ztc import Statustype, Catalogus

__all__ = [
    "Catalogus",
    "OBField",
    "OBFieldType",
    "OBList",
    "OBPagination",
    "Statustype",
    "URL",
    "ZGWError",
    "ZGWResponse",
    "Zaak",
    "as_ob_option",
]

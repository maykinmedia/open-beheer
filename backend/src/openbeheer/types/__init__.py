"""Data Transfer Object types for both ZGW APIs facing side, and our frontend."""

from ._open_beheer import (
    OBField,
    OBFieldType,
    OBList,
    OBPagination,
    OBSelection,
    as_ob_option,
)
from ._sundry import URL
from ._zgw import ZGWError, ZGWResponse
from ._zrc import Zaak
from ._ztc import Statustype

__all__ = [
    "OBField",
    "OBFieldType",
    "OBList",
    "OBPagination",
    "OBSelection",
    "Statustype",
    "URL",
    "ZGWError",
    "ZGWResponse",
    "Zaak",
    "as_ob_option",
]

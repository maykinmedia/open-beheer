"""Data Transfer Object types for both ZGW APIs facing side, and our frontend."""

from ._open_beheer import (
    OBField,
    OBFieldType,
    OBList,
    OBOption,
    OBPagedQueryParams,
    OBPagination,
    as_ob_fieldtype,
    as_ob_option,
)
from ._zgw import ZGWError, ZGWResponse
from .ztc import Catalogus, StatusType

__all__ = [
    "Catalogus",
    "OBField",
    "OBFieldType",
    "OBList",
    "OBOption",
    "OBPagination",
    "OBPagedQueryParams",
    "StatusType",
    "ZGWError",
    "ZGWResponse",
    "as_ob_fieldtype",
    "as_ob_option",
]

"""Data Transfer Object types for both ZGW APIs facing side, and our frontend."""

from ._open_beheer import (
    DetailResponse,
    DetailResponseWithoutVersions,
    ExternalServiceError,
    FrontendFieldSet,
    FrontendFieldsets,
    OBField,
    OBFieldType,
    OBList,
    OBOption,
    OBPagedQueryParams,
    OBPagination,
    VersionSummary,
    as_ob_fieldtype,
    as_ob_option,
    make_fields_optional,
    options,
)
from ._zgw import ZGWError, ZGWResponse

__all__ = [
    "DetailResponse",
    "DetailResponseWithoutVersions",
    "ExternalServiceError",
    "FrontendFieldSet",
    "FrontendFieldsets",
    "OBField",
    "OBFieldType",
    "OBList",
    "OBOption",
    "OBPagedQueryParams",
    "OBPagination",
    "VersionSummary",
    "ZGWError",
    "ZGWResponse",
    "as_ob_fieldtype",
    "as_ob_option",
    "make_fields_optional",
    "options",
]

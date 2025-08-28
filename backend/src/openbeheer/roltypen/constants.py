from openbeheer.types import FrontendFieldSet
from openbeheer.types.ztc import RolType

ROLTYPE_FIELDS = {
    field: getattr(RolType, field).__name__ for field in RolType.__struct_fields__
}

ROLTYPE_FIELDSETS = [
    (
        "Needs design",
        FrontendFieldSet(fields=[]),
    )
]

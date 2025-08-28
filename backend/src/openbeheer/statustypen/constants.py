from openbeheer.types import FrontendFieldSet
from openbeheer.types.ztc import StatusType

STATUSTYPE_FIELDS = {
    field: getattr(StatusType, field).__name__ for field in StatusType.__struct_fields__
}

STATUSTYPE_FIELDSETS = [
    (
        "Needs design",
        FrontendFieldSet(fields=[]),
    )
]

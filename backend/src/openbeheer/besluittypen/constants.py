from openbeheer.types import FrontendFieldSet
from openbeheer.types.ztc import besluittype

besluittype_FIELDS = {
    field: getattr(besluittype, field).__name__
    for field in besluittype.__struct_fields__
}

besluittype_FIELDSETS = [
    (
        "Needs design",
        FrontendFieldSet(fields=[]),
    )
]

from openbeheer.types import FrontendFieldSet
from openbeheer.types.ztc import ResultaatType

RESULTAATTYPE_FIELDS = {
    field: getattr(ResultaatType, field).__name__
    for field in ResultaatType.__struct_fields__
}

RESULTAATTYPE_FIELDSETS = [
    (
        "Needs design",
        FrontendFieldSet(fields=[]),
    )
]

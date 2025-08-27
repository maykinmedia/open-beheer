from openbeheer.types import FrontendFieldSet
from openbeheer.types.ztc import Eigenschap

EIGENSCHAPPEN_FIELDS = {
    field: getattr(Eigenschap, field).__name__ for field in Eigenschap.__struct_fields__
}

EIGENSCHAPPEN_FIELDSETS = [
    (
        "Needs design",
        FrontendFieldSet(fields=[]),
    )
]

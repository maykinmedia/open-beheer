from openbeheer.types import FrontendFieldSet
from openbeheer.types.ztc import zaakobjecttype

zaakobjecttype_FIELDS = {
    field: getattr(zaakobjecttype, field).__name__
    for field in zaakobjecttype.__struct_fields__
}

zaakobjecttype_FIELDSETS = [
    (
        "Needs design",
        FrontendFieldSet(fields=[]),
    )
]

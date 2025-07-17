from openbeheer.types import FrontendFieldSet
from openbeheer.types.ztc import InformatieObjectType

INFORMATIEOBJECTTYPE_FIELDS = {
    field: getattr(InformatieObjectType, field).__name__
    for field in InformatieObjectType.__struct_fields__
}

# TODO: No design yet
INFORMATIEOBJECTTYPE_FIELDSETS = [
    (
        "Overview",
        FrontendFieldSet(
            fields=[
                INFORMATIEOBJECTTYPE_FIELDS["omschrijving"],
                INFORMATIEOBJECTTYPE_FIELDS["vertrouwelijkheidaanduiding"],
                INFORMATIEOBJECTTYPE_FIELDS["begin_geldigheid"],
                INFORMATIEOBJECTTYPE_FIELDS["concept"],
            ]
        ),
    )
]

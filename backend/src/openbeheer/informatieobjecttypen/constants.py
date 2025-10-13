from openbeheer.types import FrontendFieldSet
from openbeheer.types import FrontendFieldsets


# TODO: No design yet
INFORMATIEOBJECTTYPE_FIELDSETS: FrontendFieldsets = [
    (
        "Overview",
        FrontendFieldSet(
            fields=[
                "omschrijving",
                "vertrouwelijkheidaanduiding",
                "begin_geldigheid",
                "concept",
            ]
        ),
    )
]

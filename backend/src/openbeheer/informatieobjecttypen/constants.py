from openbeheer.types import FrontendFieldSet, FrontendFieldsets

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

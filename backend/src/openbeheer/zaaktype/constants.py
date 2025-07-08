from __future__ import annotations

from openbeheer.types import FrontendFieldSet, FrontendFieldsets
from openbeheer.types.ztc import ZaakType

ZAAKTYPE_FIELDS = {
    field: getattr(ZaakType, field).__name__ for field in ZaakType.__struct_fields__
}

ZAAKTYPE_FIELDSETS: FrontendFieldsets = [
    (
        "Overview",
        FrontendFieldSet(
            fields=[
                ZAAKTYPE_FIELDS["identificatie"],
                ZAAKTYPE_FIELDS["omschrijving"],
                ZAAKTYPE_FIELDS["doel"],
                ZAAKTYPE_FIELDS["selectielijst_procestype"],
            ]
        ),
    ),
    (
        "General details",
        FrontendFieldSet(
            fields=[
                ZAAKTYPE_FIELDS["doel"],
                ZAAKTYPE_FIELDS["onderwerp"],
                ZAAKTYPE_FIELDS["aanleiding"],
                ZAAKTYPE_FIELDS["handeling_initiator"],
                ZAAKTYPE_FIELDS["handeling_behandelaar"],
                ZAAKTYPE_FIELDS["verantwoordelijke"],
                ZAAKTYPE_FIELDS["producten_of_diensten"],
                ZAAKTYPE_FIELDS["doorlooptijd"],
                ZAAKTYPE_FIELDS["servicenorm"],
                ZAAKTYPE_FIELDS["omschrijving"],
                ZAAKTYPE_FIELDS["omschrijving_generiek"],
                ZAAKTYPE_FIELDS["indicatie_intern_of_extern"],
                ZAAKTYPE_FIELDS["vertrouwelijkheidaanduiding"],
                ZAAKTYPE_FIELDS["publicatie_indicatie"],
                ZAAKTYPE_FIELDS["publicatietekst"],
                # TODO: fields about selectielijst_procestype that need to be expanded.
                ZAAKTYPE_FIELDS["selectielijst_procestype"],
                # TODO: expand fields of the referentie process,
                ZAAKTYPE_FIELDS["referentieproces"],
                # TODO: Zaaktype UUID
                ZAAKTYPE_FIELDS["identificatie"],
                # TODO: expand with some sort of label
                ZAAKTYPE_FIELDS["gerelateerde_zaaktypen"],
                # TODO: expand catalogus
                ZAAKTYPE_FIELDS["broncatalogus"],
            ],
        ),
    ),
]

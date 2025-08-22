# because of the runtime defined OptionalZaakType OAS generation will fail with
# ForwardRefs so no future annotations here.
# I think it could be fixed upstream
# from __future__ import annotations


from datetime import date
from typing import Annotated, Mapping
from uuid import UUID, uuid4, uuid5

from msgspec import Meta, Struct, field

from openbeheer.types import FrontendFieldSet, FrontendFieldsets, make_fields_optional
from openbeheer.types.ztc import (
    Catalogus,
    IndicatieInternOfExternEnum,
    ReferentieProces,
    VertrouwelijkheidaanduidingEnum,
    ZaakType,
)

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


class Sjabloon[T](Struct):
    "Een SJABLOON"

    naam: Annotated[
        str,
        Meta(
            description="Korte titel van het sjabloon",
            examples=[
                "Aanvraag met besluit",
                "Burgerzaken proces",
                "Productverstrekking",
            ],
            max_length=50,
        ),
    ]
    omschrijving: Annotated[
        str,
        Meta(
            description="Beknopte omschrijving van het sjabloon",
            examples=[
                "Voor processen waarbij een burger of bedrijf iets aanvraagt en daar een formeel besluit of volgt.",
                "Voor veelvoorkomende balie- of burgerprocessen.",
                "Voor het aanvragen en uitgeven van een fysiek product.",
            ],
            max_length=110,
        ),
    ]
    voorbeelden: Annotated[
        list[str],
        Meta(
            description="Voorbeelden van toepassingen",
            examples=[
                ["parkeervergunning", "evenementenvergunning"],
                ["adreswijziging", "uittreksel BRP", "reisdocument aanvragen"],
                ["afvalpas", "milieupas", "GFT-bak", "pas voor buurtcontainer"],
            ],
            min_length=2,  # If you can't come up with 2 examples. Why make a template.
            max_length=3,
        ),
    ]
    waarden: Annotated[
        T,
        Meta(
            description="De vooringevulde waarden",
        ),
    ]
    uuid: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        zaaktype_namespace = UUID("ffc8a8d8-5c2b-11f0-9c25-c952649b05dd")
        self.uuid = uuid5(zaaktype_namespace, self.naam)


OptionalZaakType = make_fields_optional(ZaakType)

# Sjabloon[OptionalZaakType] is not allowed as an annotation OptionalZaakType is a value not a type
TEMPLATES: Mapping[UUID, Sjabloon] = {
    template.uuid: template
    for template in [
        Sjabloon(
            naam="Basis",
            omschrijving="Start hier een nieuwe zaak met de juiste structuur en vooraf ingevulde velden.",
            voorbeelden=[
                "Zelf opbouwen",
                "Volledig zelf te configureren",
                "Vertrouwelijkheidaanduiding: openbaar",
            ],
            waarden=OptionalZaakType(
                omschrijving="De Zaaktype-omschrijving",
                vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.openbaar,
                doel="Een omschrijving van hetgeen beoogd is te bereiken met een zaak van dit zaaktype.",
                aanleiding="Een omschrijving van de gebeurtenis die leidt tot het starten van een ZAAK van dit ZAAKTYPE.",
                toelichting="Een eventuele toelichting op dit zaaktype",
                indicatie_intern_of_extern=IndicatieInternOfExternEnum.extern,
                handeling_initiator="Initiëren",
                onderwerp="Het onderwerp van ZAAKen van dit ZAAKTYPE.",
                handeling_behandelaar="Behandelen",
                doorlooptijd="P6W",
                opschorting_en_aanhouding_mogelijk=True,
                verlenging_mogelijk=True,
                verlengingstermijn="P2W",
                trefwoorden=["Zaaktype", "Basis"],
                publicatie_indicatie=True,
                publicatietekst="De generieke tekst van de publicatie van ZAAKen van dit ZAAKTYPE.",
                producten_of_diensten=[],
                referentieproces=make_fields_optional(ReferentieProces)(
                    naam="De naam van het Referentieproces.",
                    link="",
                ),
                verantwoordingsrelatie=[],
                selectielijst_procestype="",
                verantwoordelijke="De verantwoordelijke (soort) organisatie.",
                broncatalogus=make_fields_optional(Catalogus)(
                    url="", domein="", rsin=""
                ),
                bronzaaktype=OptionalZaakType(
                    url="", identificatie="", omschrijving=""
                ),
                begin_geldigheid=date.today(),
                versiedatum=date.today(),
                catalogus="",
                besluittypen=[],
                deelzaaktypen=[],
                gerelateerde_zaaktypen=[],
            ),
        ),
    ]
    if template.uuid
}

# because of the runtime defined OptionalZaakType OAS generation will fail with
# ForwardRefs so no future annotations here.
# I think it could be fixed upstream
# from __future__ import annotations


from typing import Annotated, Mapping
from uuid import UUID, uuid4, uuid5

from msgspec import Meta, Struct, field

from openbeheer.types import FrontendFieldSet, FrontendFieldsets, make_fields_optional
from openbeheer.types.ztc import (
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
            naam="Blanco",
            omschrijving="Voor volledige vrijheid: een leeg sjabloon zonder voorgedefiniëerde structuur.",
            voorbeelden=["van alles", "nog wat"],
            waarden=OptionalZaakType(),
        ),
        Sjabloon(
            naam="Aanvraag met besluit",
            omschrijving="Voor processen waarbij een burger of bedrijf iets aanvraagt en daar een formeel besluit of volgt.",
            voorbeelden=["parkeervergunning", "evenementenvergunning"],
            waarden=OptionalZaakType(
                omschrijving="Aanvraag voor ...",
                vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.zaakvertrouwelijk,
                doel="Besluit tot ...",
                aanleiding="",
                indicatie_intern_of_extern=IndicatieInternOfExternEnum.extern,
                handeling_initiator="Aanvraag??",
                onderwerp="",
                handeling_behandelaar="Besluitnemen??",
                doorlooptijd="6 weken",
                opschorting_en_aanhouding_mogelijk=True,
                verlenging_mogelijk=True,
                publicatie_indicatie=True,
                producten_of_diensten=[],
                referentieproces=ReferentieProces(naam="De Vries"),
                verantwoordelijke="",
                begin_geldigheid="",
                versiedatum="",
                catalogus="",
                besluittypen=[],
                gerelateerde_zaaktypen=[],
            ),
        ),
        Sjabloon(
            naam="Melding of klacht",
            omschrijving="Voor processen waarbij een burger ergens melding van maakt of klacht over indient",
            voorbeelden=[
                "melding niet opgehaald vuil",
                "overlast van horeca",
                "scheuren bij bruggen",
            ],
            waarden=OptionalZaakType(
                omschrijving="Melding van ...",
                vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.zaakvertrouwelijk,
                doel="",
                aanleiding="",
                indicatie_intern_of_extern=IndicatieInternOfExternEnum.extern,
                handeling_initiator="",
                onderwerp="",
                handeling_behandelaar="",
                doorlooptijd="",
                opschorting_en_aanhouding_mogelijk=True,
                verlenging_mogelijk=True,
                publicatie_indicatie=True,
                producten_of_diensten=[],
                referentieproces=ReferentieProces(
                    naam="Applications of process algebra",
                    link="https://cwilibrary.on.worldcat.org/oclc/24718516",
                ),
                verantwoordelijke="",
                begin_geldigheid="",
                versiedatum="",
                catalogus="",
                besluittypen=[],
                gerelateerde_zaaktypen=[],
            ),
        ),
        Sjabloon(
            naam="Interne procedure",
            omschrijving="Voor Interne gemeentelijke of organisatorische werkstromen.",
            voorbeelden=[
                "inkoopaanvraag",
                "medewerker onboarding",
                "contractverlenging",
            ],
            waarden=OptionalZaakType(
                omschrijving="",
                vertrouwelijkheidaanduiding=VertrouwelijkheidaanduidingEnum.zaakvertrouwelijk,
                doel="",
                aanleiding="",
                indicatie_intern_of_extern=IndicatieInternOfExternEnum.intern,
                handeling_initiator="",
                onderwerp="",
                handeling_behandelaar="",
                doorlooptijd="",
                opschorting_en_aanhouding_mogelijk=False,
                verlenging_mogelijk=False,
                publicatie_indicatie=True,
                producten_of_diensten=[],
                referentieproces=ReferentieProces(
                    naam="PCDA",
                    link="https://www.gemmaonline.nl/wiki/Procesarchitectuur_Besturing_en_procesverbetering#De_PDCA-cyclus",
                ),
                verantwoordelijke="",
                begin_geldigheid="",
                versiedatum="",
                catalogus="",
                besluittypen=[],
                gerelateerde_zaaktypen=[],
            ),
        ),
    ]
    if template.uuid
}

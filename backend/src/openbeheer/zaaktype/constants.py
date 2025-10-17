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
    StatusType,
    VertrouwelijkheidaanduidingEnum,
)
from openbeheer.zaaktype.api.views import ExpandableZaakTypeRequest

ZAAKTYPE_FIELDSETS: FrontendFieldsets = [
    (
        "Overview",
        FrontendFieldSet(
            fields=[
                "identificatie",
                "omschrijving",
                "doel",
                "selectielijst_procestype",
            ]
        ),
    ),
    (
        "General details",
        FrontendFieldSet(
            fields=[
                "doel",
                "onderwerp",
                "aanleiding",
                "handeling_initiator",
                "handeling_behandelaar",
                "verantwoordelijke",
                "producten_of_diensten",
                "doorlooptijd",
                "servicenorm",
                "omschrijving",
                "omschrijving_generiek",
                "indicatie_intern_of_extern",
                "vertrouwelijkheidaanduiding",
                "publicatie_indicatie",
                "publicatietekst",
                # TODO: fields about selectielijst_procestype that need to be expanded.
                "selectielijst_procestype",
                # TODO: expand fields of the referentie process,
                "referentieproces",
                # TODO: Zaaktype UUID
                "identificatie",
                # TODO: expand with some sort of label
                "gerelateerde_zaaktypen",
                # TODO: expand catalogus
                "broncatalogus",
            ],
        ),
    ),
    (
        "Statustypen",
        FrontendFieldSet(
            fields=[
                "_expand.statustypen.volgnummer",
                "_expand.statustypen.omschrijving",
                # "_expand.statustypen.omschrijving_generiek",
                # "_expand.statustypen.uuid",
            ]
        ),
    ),
    (
        "Zaakobjecttypen",
        FrontendFieldSet(
            fields=[
                # TODO: needs design
                "_expand.zaakobjecttypen.anderObjecttype",
                "_expand.zaakobjecttypen.objecttype",
                "_expand.zaakobjecttypen.relatieOmschrijving",
                "_expand.zaakobjecttypen.resultaattypen",
                "_expand.zaakobjecttypen.statustype",
                "_expand.zaakobjecttypen.beginGeldigheid",
                "_expand.zaakobjecttypen.eindeGeldigheid",
                # "_expand.zaakobjecttypen.uuid",
            ]
        ),
    ),
    (
        "ZaaktypeInformatieobjecttypen",
        FrontendFieldSet(
            fields=[
                "_expand.zaaktypeinformatieobjecttypen.volgnummer",
                "_expand.zaaktypeinformatieobjecttypen.informatieobjecttype",
                "_expand.zaaktypeinformatieobjecttypen.richting",
            ]
        ),
    ),
    (
        "Roltypen",
        FrontendFieldSet(
            fields=[
                "_expand.roltypen.omschrijving",
                "_expand.roltypen.omschrijvingGeneriek",
                # "_expand.roltypen.uuid",
            ]
        ),
    ),
    (
        "Resultaattypen",
        FrontendFieldSet(
            fields=[
                "_expand.resultaattypen.resultaattypeomschrijving",
                "_expand.resultaattypen.omschrijving",
                "_expand.resultaattypen.selectielijstklasse",
                # "_expand.resultaattypen.archiefnominatie",
                # "_expand.resultaattypen.brondatumArchiefprocedure",  # FIXME
                # "_expand.resultaattypen.uuid",
            ]
        ),
    ),
    (
        "Eigenschappen",
        FrontendFieldSet(
            fields=[
                "_expand.eigenschappen.naam",
                "_expand.eigenschappen.definitie",
                # "_expand.eigenschappen.specificatie",  # frontend has no widget
                "_expand.eigenschappen.specificatie.formaat",
                # "_expand.eigenschappen.specificatie.lengte",  # for now we set it on BFF
                # "_expand.eigenschappen.specificatie.kardinaliteit",  # for now we set it on BFF
                # "_expand.eigenschappen.uuid",
            ]
        ),
    ),
    # ( # TODO: reason: (gh-266)
    #     "Relaties",
    #     FrontendFieldSet(
    #         fields=[
    #             # TODO needs design
    #             # Assumed "Relaties" meant deelzaaktypen, went with roughly the
    #             # same fields as the zaaktype listview.
    #             # But there's a Droste-effect here we should be leveraging, maybe?
    #             "_expand.deelzaaktypen.url",
    #             "_expand.deelzaaktypen.identificatie",
    #             "_expand.deelzaaktypen.omschrijving",
    #             "_expand.deelzaaktypen.vertrouwelijkheidaanduiding",
    #             "_expand.deelzaaktypen.versiedatum",
    #             "_expand.deelzaaktypen.beginGeldigheid",
    #             "_expand.deelzaaktypen.eindeGeldigheid",
    #             "_expand.deelzaaktypen.concept",
    #         ]
    #     ),
    # ),
    # ( # TODO: reason: (gh-267)
    #     "Archivering",
    #     FrontendFieldSet(
    #         fields=[
    #             # TODO bewaartermijn etc?
    #             "_expand.selectielijstProcestype.naam",
    #             "_expand.selectielijstProcestype.nummer",
    #             "_expand.selectielijstProcestype.jaar",
    #             "_expand.selectielijstProcestype.omschrijving",
    #             "_expand.selectielijstProcestype.toelichting",
    #             "_expand.selectielijstProcestype.procesobject",
    #             "_expand.selectielijstProcestype.url",
    #         ]
    #     ),
    # ),
    # TODO??: This probably needs some careful UX design, there's a
    # Many to Many (zaaktypen, besluittypen, resultaattypen, informatieobjecttypen)
    # naive editing in a grid on a tab under a zaaktype may be disorienting
    # (
    #     "Besluittypen",
    #     FrontendFieldSet(
    #         fields=[
    #             "_expand.besluittypen.catalogus",
    #             "_expand.besluittypen.publicatieIndicatie",
    #             "_expand.besluittypen.informatieobjecttypen",
    #             "_expand.besluittypen.beginGeldigheid",
    #             "_expand.besluittypen.url",
    #             "_expand.besluittypen.zaaktypen",
    #             "_expand.besluittypen.omschrijving",
    #             "_expand.besluittypen.omschrijvingGeneriek",
    #             "_expand.besluittypen.besluitcategorie",
    #             "_expand.besluittypen.reactietermijn",
    #             "_expand.besluittypen.publicatietekst",
    #             "_expand.besluittypen.publicatietermijn",
    #             "_expand.besluittypen.toelichting",
    #             "_expand.besluittypen.eindeGeldigheid",
    #             "_expand.besluittypen.concept",
    #             "_expand.besluittypen.resultaattypen",
    #             "_expand.besluittypen.resultaattypenOmschrijving",
    #             "_expand.besluittypen.vastgelegdIn",
    #             "_expand.besluittypen.beginObject",
    #             "_expand.besluittypen.eindeObject",
    #             "_expand.besluittypen.uuid",
    #         ]
    #     ),
    # ),
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


OptionalZaakType = make_fields_optional(ExpandableZaakTypeRequest)

waarden_dict = {
    "omschrijving": "De Zaaktype-omschrijving",
    "vertrouwelijkheidaanduiding": VertrouwelijkheidaanduidingEnum.openbaar,
    "doel": "Een omschrijving van hetgeen beoogd is te bereiken met een zaak van dit zaaktype.",
    "aanleiding": "Een omschrijving van de gebeurtenis die leidt tot het starten van een ZAAK van dit ZAAKTYPE.",
    "toelichting": "Een eventuele toelichting op dit zaaktype",
    "indicatie_intern_of_extern": IndicatieInternOfExternEnum.extern,
    "handeling_initiator": "Initiëren",
    "onderwerp": "Het onderwerp van ZAAKen van dit ZAAKTYPE.",
    "handeling_behandelaar": "Behandelen",
    "doorlooptijd": "P6W",
    "opschorting_en_aanhouding_mogelijk": True,
    "verlenging_mogelijk": True,
    "verlengingstermijn": "P2W",
    "trefwoorden": ["Zaaktype", "Basis"],
    "publicatie_indicatie": True,
    "publicatietekst": "De generieke tekst van de publicatie van ZAAKen van dit ZAAKTYPE.",
    "producten_of_diensten": [],
    "referentieproces": make_fields_optional(ReferentieProces)(
        naam="De naam van het Referentieproces.",
        link="",
    ),
    "verantwoordingsrelatie": [],
    "selectielijst_procestype": "",
    "verantwoordelijke": "De verantwoordelijke (soort) organisatie.",
    "broncatalogus": make_fields_optional(Catalogus)(url="", domein="", rsin=""),
    "bronzaaktype": OptionalZaakType(identificatie="", omschrijving=""),
    "begin_geldigheid": date.today(),
    "versiedatum": date.today(),
    "catalogus": "",
    "besluittypen": [],
    "deelzaaktypen": [],
    "gerelateerde_zaaktypen": [],
}

TEMPLATE_BASE: Sjabloon = Sjabloon(
    naam="Basis",
    omschrijving="Start hier een nieuwe zaak met de juiste structuur en vooraf ingevulde velden.",
    voorbeelden=[
        "Zelf opbouwen",
        "Volledig zelf te configureren",
        "Vertrouwelijkheidaanduiding: openbaar",
    ],
    waarden=OptionalZaakType(**waarden_dict),
)

TEMPLATE_STATUSES = Sjabloon(
    naam="Met statustypen",
    omschrijving="Met statustypen.",
    voorbeelden=[
        "Ingediend",
        "In behandeling",
        "Afgerond",
    ],
    waarden=OptionalZaakType(
        **{
            **waarden_dict,
            "_expand": {
                "statustypen": [
                    StatusType(
                        volgnummer=1,
                        omschrijving="Ingediend",
                        omschrijving_generiek="Ingediend",
                        statustekst="Ingediend",
                        informeren=False,
                        checklistitem_statustype=[],
                        zaaktype="",
                    ),
                    StatusType(
                        volgnummer=2,
                        omschrijving="In behandeling",
                        omschrijving_generiek="In behandeling",
                        statustekst="In behandeling",
                        informeren=False,
                        checklistitem_statustype=[],
                        zaaktype="",
                    ),
                    StatusType(
                        volgnummer=3,
                        omschrijving="Afgehandeld",
                        omschrijving_generiek="Afgehandeld",
                        statustekst="Afgehandeld",
                        informeren=False,
                        checklistitem_statustype=[],
                        zaaktype="",
                    ),
                ],
            },
        }
    ),
)

TEMPLATES: list[Sjabloon] = [TEMPLATE_BASE, TEMPLATE_STATUSES]

# Sjabloon[OptionalZaakType] is not allowed as an annotation OptionalZaakType is a value not a type
TEMPLATE_MAPPING: Mapping[UUID, Sjabloon] = {
    template.uuid: template for template in TEMPLATES if template.uuid
}

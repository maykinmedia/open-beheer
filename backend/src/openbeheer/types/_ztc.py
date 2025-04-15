"""Zaaktype Component DTO's

These are the types of the responses of the ZTC API.
"""

import datetime
import enum
from typing import assert_never

# Import gt as __, _ will clash...
# TODO: test if this is lazy enough or whether we need gettext_lazy and a box of tissues to dry my type error tears
from django.utils.translation import gettext as __

from msgspec import UNSET, Struct, UnsetType

from ._open_beheer import OBOption, as_ob_option
from ._sundry import URL

__all__ = []


class Archiefstatus(enum.StrEnum):
    "vng_api_common.Archiefstatus"

    # not really a ztc type, but this seemed close enough.

    nog_te_archiveren = enum.auto()
    gearchiveerd = enum.auto()
    gearchiveerd_procestermijn_onbekend = enum.auto()
    overgedragen = enum.auto()


@as_ob_option.register
def _(arg: Archiefstatus, /) -> OBOption[Archiefstatus]:
    # map Archiefstatus._members to labels copied from vng_api_common
    option = lambda label: OBOption(label=__(label), value=arg)

    # default strings copied from vng_api_common, which Open Zaak also uses.
    # didn't want to require the whole of that library (yet)
    match arg:
        case arg.nog_te_archiveren:
            return option(
                "De zaak cq. het zaakdossier is nog niet als geheel gearchiveerd."
            )
        case arg.gearchiveerd:
            return option(
                "De zaak cq. het zaakdossier is als geheel niet-wijzigbaar bewaarbaar gemaakt."
            )
        case arg.gearchiveerd_procestermijn_onbekend:
            return option(
                "De zaak cq. het zaakdossier is als geheel niet-wijzigbaar bewaarbaar gemaakt maar de vernietigingsdatum "
                "kan nog niet bepaald worden."
            )
        case arg.overgedragen:
            return option(
                "De zaak cq. het zaakdossier is overgebracht naar een archiefbewaarplaats."
            )
        case _:
            assert_never(arg)


class Catalogus(Struct):
    """
    ZTC.CATALOGUS

    Attributes:
        domein: Een afkorting waarmee wordt aangegeven voor welk domein in een CATALOGUS ZAAKTYPEn zijn
            uitgewerkt.
        rsin: Het door een kamer toegekend uniek nummer voor de INGESCHREVEN NIET-NATUURLIJK PERSOON die de
            eigenaar is van een CATALOGUS.
        contactpersoon_beheer_naam: De naam van de contactpersoon die verantwoordelijk is voor het beheer van de
            CATALOGUS.
        url: URL-referentie naar dit object. Dit is de unieke identificatie en locatie van dit
            object.
        contactpersoon_beheer_telefoonnummer: Het telefoonnummer van de contactpersoon die
            verantwoordelijk is voor het beheer van de CATALOGUS.
        contactpersoon_beheer_emailadres: Het emailadres van de contactpersoon die verantwoordelijk
            is voor het beheer van de CATALOGUS.
        zaaktypen: URL-referenties naar ZAAKTYPEn die in deze CATALOGUS worden ontsloten.
        besluittypen: URL-referenties naar BESLUITTYPEn die in deze CATALOGUS worden
            ontsloten.
        informatieobjecttypen: URL-referenties naar INFORMATIEOBJECTTYPEn die in deze
            CATALOGUS worden ontsloten.
        naam: De benaming die is gegeven aan de zaaktypecatalogus.
        versie: Versie-aanduiding van de van toepassing zijnde zaaktypecatalogus.
        begindatum_versie: Datum waarop de versie van de zaaktypecatalogus van
            toepassing is geworden.
    """

    domein: str
    rsin: str
    contactpersoon_beheer_naam: str
    url: UnsetType | URL = UNSET
    contactpersoon_beheer_telefoonnummer: UnsetType | str = UNSET
    contactpersoon_beheer_emailadres: UnsetType | str = UNSET
    zaaktypen: UnsetType | list[str] = UNSET
    besluittypen: UnsetType | list[str] = UNSET
    informatieobjecttypen: UnsetType | list[str] = UNSET
    naam: UnsetType | str = UNSET
    versie: UnsetType | str = UNSET
    begindatum_versie: None | UnsetType | datetime.date = UNSET


class Statustype(Struct, rename="camel"):
    "ZTC.STATUSTYPE"

    url: URL
    omschrijving: str
    omschrijving_generiek: str
    statustekst: str
    # zaaktype_identificatie: str
    volgnummer: int
    # catalogus: URL
    # begin_geldigheid: datetime.date
    # einde_geldigheid: datetime.date
    # begin_object: datetime.date
    # einde_object: datetime.date


@as_ob_option.register
def _(arg: Statustype, /) -> OBOption[URL]:
    # TODO: don't return foreign url
    return OBOption(label=arg.omschrijving, value=arg.url)


class Zaaktype(Struct):
    "ZTC.ZAAKTYPE"

    url: URL
    identificatie: str
    beginGeldigheid: datetime.date
    statustypen: list[str]
    resultaattypen: list[str]
    omschrijving: str | None = None

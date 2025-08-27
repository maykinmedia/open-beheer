import string
from dataclasses import dataclass
from random import choice
from typing import Literal, Mapping, Sequence, Type

from msgspec import to_builtins
from msgspec.json import decode

from openbeheer.clients import ztc_client
from openbeheer.types import ResultaatTypeWithUUID
from openbeheer.types._open_beheer import EigenschapWithUUID, ZaakTypeWithUUID
from openbeheer.types.ztc import (
    BesluitType,
    Catalogus,
    EigenschapSpecificatie,
    EigenschapSpecificatieRequest,
    FormaatEnum,
    InformatieObjectType,
    RolType,
    StatusType,
    ZaakTypeInformatieObjectType,
)

type _JSONEncodable = (
    None
    | bool
    | int
    | float
    | str
    | Sequence[_JSONEncodable]
    | Mapping[str, _JSONEncodable]
)


@dataclass
class OpenZaakDataCreationHelper:
    service_identifier: str

    def _create_resource[T](
        self,
        data: Mapping[str, _JSONEncodable],
        resource_path: str,
        resource_type: Type[T],
    ) -> T:
        with ztc_client("OZ") as client:
            response = client.post(resource_path, json=data)

            if response.status_code == 400:
                raise Exception(decode(response.content))

            response.raise_for_status()

        return decode(
            response.content,
            type=resource_type,
            strict=False,
        )

    def _get_catalogus(self, catalogus="", **_) -> str:
        assert (url := catalogus or self.create_catalogus().url)
        return url

    def _get_zaaktype(self, zaaktype="", **_) -> str:
        assert (url := zaaktype or self.create_zaaktype().url)
        return url

    # Can't use the Patched requests for the type of the overrides, because the unset
    # values are filled with the default values  when converting to the dict type
    def create_informatieobjecttype(
        self, catalogus: str = "", **overrides: _JSONEncodable
    ) -> InformatieObjectType:
        data: dict[str, _JSONEncodable] = {
            "catalogus": self._get_catalogus(catalogus),
            "omschrijving": "Omschrijving A",
            "vertrouwelijkheidaanduiding": "openbaar",
            "beginGeldigheid": "2025-07-01",
            "informatieobjectcategorie": "Blue",
        } | overrides

        return self._create_resource(
            data, "informatieobjecttypen", InformatieObjectType
        )

    def create_catalogus(self, **overrides: _JSONEncodable) -> Catalogus:
        data: dict[str, _JSONEncodable] = {
            "domein": "".join([choice(string.ascii_uppercase) for _ in range(5)]),
            "rsin": "123456782",
            "contactpersoonBeheerNaam": "Ubaldo",
            "naam": "Test catalogus",
        } | overrides

        return self._create_resource(data, "catalogussen", Catalogus)

    def create_statustype(
        self, zaaktype: str = "", **overrides: _JSONEncodable
    ) -> StatusType:
        data: dict[str, _JSONEncodable] = {
            "omschrijving": "Ontvangen",
            "zaaktype": zaaktype,
            "volgnummer": 1,
            "omschrijving_generiek": "",
            "statustekst": "",
            "informeren": False,
            "checklistitem_statustype": [],
        } | overrides

        return self._create_resource(data, "statustypen", StatusType)

    def relate_zaaktype_informatieobjecttype(
        self,
        zaaktype_url: str,
        informatieobjecttype_url: str,
        **overrides: _JSONEncodable,
    ) -> ZaakTypeInformatieObjectType:
        data: dict[str, _JSONEncodable] = {
            "zaaktype": zaaktype_url,
            "informatieobjecttype": informatieobjecttype_url,
            "volgnummer": 1,
            "richting": "inkomend",
        } | overrides

        return self._create_resource(
            data, "zaaktype-informatieobjecttypen", ZaakTypeInformatieObjectType
        )

    def create_zaaktype(
        self, catalogus: str = "", **overrides: _JSONEncodable
    ) -> ZaakTypeWithUUID:
        data: dict[str, _JSONEncodable] = {
            "omschrijving": "Another test zaaktype",
            "vertrouwelijkheidaanduiding": "geheim",
            "doel": "New Zaaktype 001",
            "aanleiding": "New Zaaktype 001",
            "indicatieInternOfExtern": "intern",
            "handelingInitiator": "aanvragen",
            "onderwerp": "New Zaaktype 001",
            "handelingBehandelaar": "handelin",
            "doorlooptijd": "P40D",
            "opschortingEnAanhoudingMogelijk": False,
            "verlengingMogelijk": True,
            "verlengingstermijn": "P40D",
            "publicatieIndicatie": False,
            "productenOfDiensten": ["https://example.com/product/321"],
            "referentieproces": {"naam": "ReferentieProces 1"},
            "verantwoordelijke": "200000000",
            "beginGeldigheid": "2025-06-19",
            "versiedatum": "2025-06-19",
            "catalogus": self._get_catalogus(catalogus),
            "besluittypen": [],
            "gerelateerdeZaaktypen": [],
            "selectielijstProcestype": "https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0",
        } | overrides

        return self._create_resource(data, "zaaktypen", ZaakTypeWithUUID)

    def create_resultaattype(
        self,
        zaaktype: str = "",
        **overrides: _JSONEncodable,
    ) -> ResultaatTypeWithUUID:
        data: dict[str, _JSONEncodable] = {
            "zaaktype": self._get_zaaktype(zaaktype),
            "omschrijving": "Gegrond",
            "resultaattypeomschrijving": "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/3a0a9c3c-0847-4e7e-b7d9-765b9434094c",
            "selectielijstklasse": "https://selectielijst.openzaak.nl/api/v1/resultaten/8af64c99-a168-40dd-8afd-9fbe0597b6dc",
            "archiefnominatie": "vernietigen",
            "brondatumArchiefprocedure": {
                "afleidingswijze": "afgehandeld",
                "procestermijn": None,
                "datumkenmerk": "",
                "einddatumBekend": False,
                "objecttype": "",
                "registratie": "",
            },
        } | overrides

        return self._create_resource(data, "resultaattypen", ResultaatTypeWithUUID)

    def create_roltype(
        self,
        zaaktype: str = "",
        omschrijvingGeneriek: Literal[  # noqa: N803
            "adviseur",
            "behandelaar",
            "belanghebbende",
            "beslisser",
            "initiator",
            "klantcontacter",
            "mede_initiator",
            "zaakcoordinator",
        ] = "initiator",
        **overrides: _JSONEncodable,
    ) -> RolType:
        data: dict[str, _JSONEncodable] = {
            "zaaktype": self._get_zaaktype(zaaktype),
            "omschrijving": "Vastgesteld",
            "omschrijvingGeneriek": omschrijvingGeneriek,
            **overrides,
        }
        return self._create_resource(data, "roltypen", RolType)

    def create_besluittype(self, **overrides: _JSONEncodable) -> BesluitType:
        return self._create_resource(
            {
                # "zaaktypen": [],
                "publicatieIndicatie": False,
                "informatieobjecttypen": [],
                "beginGeldigheid": "2025-06-19",
                **overrides,
            },
            "besluittypen",
            BesluitType,
        )

    def create_eigenschap(self, **overrides: _JSONEncodable) -> EigenschapWithUUID:
        return self._create_resource(
            {
                # "zaaktypen": [],
                "naam": "Henk de Vries",
                "definitie": "Niet de broer van Henk de Vries",
                "specificatie": to_builtins(
                    EigenschapSpecificatieRequest(
                        formaat=FormaatEnum.tekst,
                        lengte="1",
                        kardinaliteit="1",
                        groep="de De Vriesjes",  # required???
                        waardenverzameling=[],  # required???
                    )
                ),
                **overrides,
            },
            "eigenschappen",
            EigenschapWithUUID,
        )

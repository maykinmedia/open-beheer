from dataclasses import dataclass
from typing import Type
from msgspec.json import decode
from openbeheer.clients import ztc_client
from openbeheer.types.ztc import (
    Catalogus,
    InformatieObjectType,
    ResultaatType,
    RolType,
    ZaakType,
    ZaakTypeInformatieObjectType,
)
from random import choice
import string


@dataclass
class OpenZaakDataCreationHelper:
    service_identifier: str

    def _create_resource[T](
        self, data: dict[str, str], resource_path: str, resource_type: Type[T]
    ) -> T:
        with ztc_client("OZ") as client:
            response = client.post(resource_path, json=data)

            response.raise_for_status()

        return decode(
            response.content,
            type=resource_type,
            strict=False,
        )

    def _get_catalogus(self, data: dict | None = None) -> str:
        catalogus_url = data and data.get("catalogus", "")
        if not catalogus_url:
            catalogus = self.create_catalogus()
            catalogus_url = catalogus.url
            assert catalogus_url

        assert isinstance(catalogus_url, str)
        return catalogus_url

    def _get_zaaktype(self, data: dict | None = None) -> str:
        zaaktype_url = data and data.get("zaaktype", "")
        if not zaaktype_url:
            zaaktype = self.create_zaaktype()
            zaaktype_url = zaaktype.url
            assert zaaktype_url

        assert isinstance(zaaktype_url, str)
        return zaaktype_url

    # Can't use the Patched requests for the type of the overrides, because the unset
    # values are filled with the default values  when converting to the dict type
    def create_informatieobjecttype(
        self, overrides: dict | None = None
    ) -> InformatieObjectType:
        data = {
            "catalogus": self._get_catalogus(overrides),
            "omschrijving": "Omschrijving A",
            "vertrouwelijkheidaanduiding": "openbaar",
            "beginGeldigheid": "2025-07-01",
            "informatieobjectcategorie": "Blue",
        }
        if overrides:
            data.update(overrides)

        return self._create_resource(
            data, "informatieobjecttypen", InformatieObjectType
        )

    def create_catalogus(self, overrides: dict | None = None) -> Catalogus:
        data = {
            "domein": "".join([choice(string.ascii_uppercase) for _ in range(5)]),
            "rsin": "123456782",
            "contactpersoonBeheerNaam": "Ubaldo",
            "naam": "Test catalogus",
        }
        if overrides:
            data.update(overrides)

        return self._create_resource(data, "catalogussen", Catalogus)

    def relate_zaaktype_informatieobjecttype(
        self,
        zaaktype_url: str,
        informatieobjecttype_url: str,
        overrides: dict | None = None,
    ) -> ZaakTypeInformatieObjectType:
        data = {
            "zaaktype": zaaktype_url,
            "informatieobjecttype": informatieobjecttype_url,
            "volgnummer": 1,
            "richting": "inkomend",
        }
        if overrides:
            data.update(overrides)

        return self._create_resource(
            data, "zaaktype-informatieobjecttypen", ZaakTypeInformatieObjectType
        )

    def create_zaaktype(self, overrides: dict | None = None) -> ZaakType:
        data = {
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
            "catalogus": self._get_catalogus(overrides),
            "besluittypen": [],
            "gerelateerdeZaaktypen": [],
            "selectielijstProcestype": "https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0",
        }
        if overrides:
            data.update(overrides)

        return self._create_resource(data, "zaaktypen", ZaakType)

    def create_resultaattype(self, overrides: dict | None = None) -> ResultaatType:
        data = {
            "zaaktype": self._get_zaaktype(overrides),
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
        }
        if overrides:
            data.update(overrides)

        return self._create_resource(data, "resultaattypen", ResultaatType)

    def create_roltype(self, overrides: dict | None = None) -> RolType:
        data = {
            "zaaktype": self._get_zaaktype(overrides),
            "omschrijving": "Vastgesteld",
            "omschrijvingGeneriek": "Beleidsplan met externe werking",
        }

        if overrides:
            data.update(overrides)

        return self._create_resource(data, "roltypen", RolType)

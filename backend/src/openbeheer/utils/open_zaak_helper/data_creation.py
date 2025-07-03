from dataclasses import dataclass
from typing import Type
from uuid import UUID
from msgspec import UNSET, UnsetType
from msgspec.json import decode
from openbeheer.clients import ztc_client
from openbeheer.types.ztc import (
    Catalogus,
    InformatieObjectType,
    ZaakType,
    ZaakTypeInformatieObjectType,
)
from random import choice
import string


@dataclass
class OpenZaakDataCreationHelper:
    service_identifier: str
    catalogus_uuid: UUID | UnsetType = UNSET

    @property
    def catalogus_url(self) -> str:
        if not self.catalogus_uuid:
            return ""

        with ztc_client(self.service_identifier) as client:
            return f"{client.base_url}catalogussen/{self.catalogus_uuid}"

    def set_catalogus_uuid(self, catalogus_uuid: UUID) -> None:
        self.catalogus_uuid = catalogus_uuid

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
        catalogus_url = self.catalogus_url or (data and data.get("catalogus", ""))
        if not catalogus_url:
            catalogus = self.create_catalogus()
            catalogus_url = catalogus.url
            assert catalogus_url

        assert isinstance(catalogus_url, str)
        return catalogus_url

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
        }
        if overrides:
            data.update(overrides)

        return self._create_resource(data, "zaaktypen", ZaakType)

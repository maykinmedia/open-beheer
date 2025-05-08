import { TypedField } from "@maykin-ui/admin-ui";
import { ZaakType } from "~/types";

export const FIXTURE_ZAAKTYPE_FIELDS: TypedField<ZaakType>[] = [
  {
    filterable: false,
    name: "url",
    type: "string",
  },
  {
    filterable: true,
    name: "identificatie",
    type: "string",
  },
  {
    filterable: false,
    name: "omschrijving",
    type: "string",
  },
  {
    filterable: false,
    name: "omschrijvingGeneriek",
    type: "string",
  },
  {
    options: [
      {
        label: "openbaar",
        value: "openbaar",
      },
      {
        label: "beperkt openbaar",
        value: "beperkt_openbaar",
      },
      {
        label: "intern",
        value: "intern",
      },
      {
        label: "zaakvertrouwelijk",
        value: "zaakvertrouwelijk",
      },
      {
        label: "vertrouwelijk",
        value: "vertrouwelijk",
      },
      {
        label: "confidentieel",
        value: "confidentieel",
      },
      {
        label: "geheim",
        value: "geheim",
      },
      {
        label: "zeer geheim",
        value: "zeer_geheim",
      },
    ],
    filterable: false,
    name: "vertrouwelijkheidaanduiding",
    type: "string",
  },
  {
    filterable: false,
    name: "doel",
    type: "string",
  },
  {
    filterable: false,
    name: "aanleiding",
    type: "string",
  },
  {
    filterable: false,
    name: "toelichting",
    type: "string",
  },
  {
    options: [
      {
        label: "intern",
        value: "intern",
      },
      {
        label: "extern",
        value: "extern",
      },
    ],
    filterable: false,
    name: "indicatieInternOfExtern",
    type: "string",
  },
  {
    filterable: false,
    name: "handelingInitiator",
    type: "string",
  },
  {
    filterable: false,
    name: "onderwerp",
    type: "string",
  },
  {
    filterable: false,
    name: "handelingBehandelaar",
    type: "string",
  },
  {
    filterable: false,
    name: "doorlooptijd",
    type: "string",
  },
  {
    filterable: false,
    name: "servicenorm",
    type: "string",
  },
  {
    filterable: false,
    name: "opschortingEnAanhoudingMogelijk",
    type: "boolean",
  },
  {
    filterable: false,
    name: "verlengingMogelijk",
    type: "boolean",
  },
  {
    filterable: false,
    name: "verlengingstermijn",
    type: "string",
  },
  {
    filterable: true,
    name: "trefwoorden",
    type: "array",
  },
  {
    filterable: false,
    name: "publicatieIndicatie",
    type: "boolean",
  },
  {
    filterable: false,
    name: "publicatietekst",
    type: "string",
  },
  {
    filterable: false,
    name: "verantwoordingsrelatie",
    type: "array",
  },
  {
    filterable: false,
    name: "productenOfDiensten",
    type: "array",
  },
  {
    filterable: false,
    name: "selectielijstProcestype",
    type: "string",
  },
  {
    filterable: false,
    name: "referentieproces",
    type: "object",
  },
  {
    filterable: false,
    name: "concept",
    type: "boolean",
  },
  {
    filterable: false,
    name: "verantwoordelijke",
    type: "string",
  },
  {
    filterable: false,
    name: "broncatalogus",
    type: "object",
  },
  {
    filterable: false,
    name: "bronzaaktype",
    type: "object",
  },
  {
    filterable: false,
    name: "beginGeldigheid",
    type: "string",
  },
  {
    filterable: false,
    name: "eindeGeldigheid",
    type: "string",
  },
  {
    filterable: false,
    name: "versiedatum",
    type: "string",
  },
  {
    filterable: false,
    name: "beginObject",
    type: "string",
  },
  {
    filterable: false,
    name: "eindeObject",
    type: "string",
  },
  {
    filterable: true,
    name: "catalogus",
    type: "string",
  },
  {
    filterable: false,
    name: "statustypen",
    type: "array",
  },
  {
    filterable: false,
    name: "resultaattypen",
    type: "array",
  },
  {
    filterable: false,
    name: "eigenschappen",
    type: "array",
  },
  {
    filterable: false,
    name: "informatieobjecttypen",
    type: "array",
  },
  {
    filterable: false,
    name: "roltypen",
    type: "array",
  },
  {
    filterable: false,
    name: "besluittypen",
    type: "array",
  },
  {
    filterable: false,
    name: "deelzaaktypen",
    type: "array",
  },
  {
    filterable: false,
    name: "gerelateerdeZaaktypen",
    type: "array",
  },
  {
    filterable: false,
    name: "zaakobjecttypen",
    type: "array",
  },
];

export const FIXTURE_ZAAKTYPE = {
  uuid: "c1a3f1d0-1234-4bcd-a567-abcdef123456",
  url: "https://demo.openzaak.nl/catalogi/api/v1/zaaktypen/c1a3f1d0-1234-4bcd-a567-abcdef123456",
  identificatie: "ZAAKTYPE-001",
  omschrijving: "Aanvraag parkeervergunning",
  doel: "Het afhandelen van aanvragen voor parkeervergunningen",
  verantwoordelijke: "Gemeente Stad",
  publicatieIndicatie: true,
  datumBeginGeldigheid: "2023-01-01",
  datumEindeGeldigheid: null,
  zaakcategorie: "Verkeer en vervoer",
  broncatalogus: "https://example.com/catalogus/1",
};

export const FIXTURE_ZAAKTYPEN: ZaakType[] = [
  {
    uuid: "c1a3f1d0-1234-4bcd-a567-abcdef123456",
    url: "https://demo.openzaak.nl/catalogi/api/v1/zaaktypen/c1a3f1d0-1234-4bcd-a567-abcdef123456",
    identificatie: "ZAAKTYPE-001",
    omschrijving: "Aanvraag parkeervergunning",
    doel: "Het afhandelen van aanvragen voor parkeervergunningen",
    verantwoordelijke: "Gemeente Stad",
    publicatieIndicatie: true,
    datumBeginGeldigheid: "2023-01-01",
    datumEindeGeldigheid: null,
    zaakcategorie: "Verkeer en vervoer",
    broncatalogus: "https://example.com/catalogus/1",
  },
  {
    uuid: "b2d2a2c0-5678-4ef0-9123-fedcba654321",
    url: "https://demo.openzaak.nl/catalogi/api/v1/zaaktypen/b2d2a2c0-5678-4ef0-9123-fedcba654321",
    identificatie: "ZAAKTYPE-002",
    omschrijving: "Melding openbare ruimte",
    doel: "Het behandelen van meldingen over de openbare ruimte",
    verantwoordelijke: "Afdeling Beheer Openbare Ruimte",
    publicatieIndicatie: false,
    datumBeginGeldigheid: "2022-06-15",
    datumEindeGeldigheid: "2024-12-31",
    zaakcategorie: "Openbare ruimte",
    broncatalogus: "https://example.com/catalogus/2",
  },
  {
    uuid: "e3b9d8f4-7890-4aaa-8888-1234abcd5678",
    url: "https://demo.openzaak.nl/catalogi/api/v1/zaaktypen/e3b9d8f4-7890-4aaa-8888-1234abcd5678",
    identificatie: "ZAAKTYPE-003",
    omschrijving: "Bezwaar tegen besluit",
    doel: "Het behandelen van bezwaarschriften",
    verantwoordelijke: "Juridische Zaken",
    publicatieIndicatie: true,
    datumBeginGeldigheid: "2024-04-01",
    datumEindeGeldigheid: null,
    zaakcategorie: "Bestuur en beleid",
    broncatalogus: "https://example.com/catalogus/3",
  },
];

export default FIXTURE_ZAAKTYPEN;

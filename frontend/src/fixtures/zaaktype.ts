import { FieldSet, TypedField } from "@maykin-ui/admin-ui";
import { components } from "~/types";

export const FIXTURE_ZAAKTYPE: components["schemas"]["ExpandableZaakType"] = {
  uuid: "be210495-20b6-48ff-8d3d-3e44f74c43a4",
  _expand: {
    besluittypen: [],
    statustypen: [
      {
        uuid: "9438e56a-5d78-4dc8-9d9a-2404781f818d",
        omschrijving: "Statustype Completed",
        zaaktype:
          "http://localhost:8003/catalogi/api/v1/zaaktypen/be210495-20b6-48ff-8d3d-3e44f74c43a4",
        volgnummer: 1,
        url: "http://localhost:8003/catalogi/api/v1/statustypen/9438e56a-5d78-4dc8-9d9a-2404781f818d",
        omschrijvingGeneriek: "",
        statustekst: "",
        zaaktypeIdentificatie: "ZAAKTYPE-2018-0000000001",
        isEindstatus: true,
        informeren: false,
        doorlooptijd: null,
        toelichting: null,
        checklistitemStatustype: [],
        catalogus:
          "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
        eigenschappen: [],
        zaakobjecttypen: [],
        beginGeldigheid: null,
        eindeGeldigheid: null,
        beginObject: null,
        eindeObject: null,
      },
    ],
    resultaattypen: [
      {
        uuid: "12903100-b7a0-4441-9645-eda7df2ad106",
        zaaktype:
          "http://localhost:8003/catalogi/api/v1/zaaktypen/be210495-20b6-48ff-8d3d-3e44f74c43a4",
        omschrijving: "Verwerkt",
        resultaattypeomschrijving:
          "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/f33dbd16-68ae-4820-acb5-5f437bca5edb",
        selectielijstklasse:
          "https://selectielijst.openzaak.nl/api/v1/resultaten/cc5ae4e3-a9e6-4386-bcee-46be4986a829",
        url: "http://localhost:8003/catalogi/api/v1/resultaattypen/12903100-b7a0-4441-9645-eda7df2ad106",
        zaaktypeIdentificatie: "ZAAKTYPE-2018-0000000001",
        omschrijvingGeneriek: "",
        toelichting: "",
        archiefnominatie: "",
        archiefactietermijn: null,
        brondatumArchiefprocedure: {
          afleidingswijze: "afgehandeld",
          datumkenmerk: "",
          einddatumBekend: false,
          objecttype: "",
          registratie: "",
          procestermijn: null,
        },
        procesobjectaard: "",
        indicatieSpecifiek: null,
        procestermijn: null,
        catalogus:
          "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
        besluittypen: [],
        besluittypeOmschrijving: [],
        informatieobjecttypen: [],
        informatieobjecttypeOmschrijving: [],
        beginGeldigheid: null,
        eindeGeldigheid: null,
        beginObject: null,
        eindeObject: null,
      },
    ],
    eigenschappen: [],
    informatieobjecttypen: [
      {
        uuid: "a8089bdf-72d3-414f-a9cd-953cfa602b6c",
        catalogus:
          "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
        omschrijving: "Informatie object type 0",
        vertrouwelijkheidaanduiding: "openbaar",
        beginGeldigheid: "2018-01-01",
        informatieobjectcategorie: "stock",
        url: "http://localhost:8003/catalogi/api/v1/informatieobjecttypen/a8089bdf-72d3-414f-a9cd-953cfa602b6c",
        eindeGeldigheid: null,
        concept: false,
        besluittypen: [],
        trefwoord: [],
        omschrijvingGeneriek: {
          informatieobjecttypeOmschrijvingGeneriek: "bill",
          definitieInformatieobjecttypeOmschrijvingGeneriek:
            "Bank sound west control fly Mrs. West their some pressure. Many often various guess first move visit group.",
          herkomstInformatieobjecttypeOmschrijvingGeneriek: "ZSWuoDPOIaWF",
          hierarchieInformatieobjecttypeOmschrijvingGeneriek: "until",
          opmerkingInformatieobjecttypeOmschrijvingGeneriek: "",
        },
        zaaktypen: [
          "http://localhost:8003/catalogi/api/v1/zaaktypen/be210495-20b6-48ff-8d3d-3e44f74c43a4",
        ],
        beginObject: "2018-01-01",
        eindeObject: null,
      },
    ],
    roltypen: [],
    deelzaaktypen: [],
    zaakobjecttypen: [],
    selectielijstProcestype: {
      nummer: 1,
      jaar: 2020,
      naam: "Instellen en inrichten organisatie",
      omschrijving: "Instellen en inrichten organisatie",
      toelichting:
        "Dit procestype betreft het instellen van een nieuw organisatieonderdeel of een nieuwe orgaan waar het orgaan in deelneemt. Dit procestype betreft eveneens het inrichten van het eigen orgaan. Dit kan kleinschalig plaatsvinden bijvoorbeeld het wijzigen van de uitvoering van een wettelijke taak of grootschalig wanneer er een organisatiewijziging wordt doorgevoerd.",
      procesobject: "De vastgestelde organisatie inrichting",
      url: "https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0",
    },
  },
  omschrijving: "brand world-class initiatives",
  vertrouwelijkheidaanduiding: "openbaar",
  doel: "Trouble red compare produce animal. Everything today Democrat student enter. By probably adult.",
  aanleiding: "Couple toward trip old nice memory system instead.",
  indicatieInternOfExtern: "extern",
  handelingInitiator: "indienen",
  onderwerp: "Evenementvergunning",
  handelingBehandelaar: "uitvoeren",
  doorlooptijd: "P30D",
  opschortingEnAanhoudingMogelijk: true,
  verlengingMogelijk: false,
  publicatieIndicatie: true,
  productenOfDiensten: ["https://example.com/product/123"],
  referentieproces: {
    naam: "ReferentieProces 0",
    link: "",
  },
  verantwoordelijke: "100000000",
  beginGeldigheid: "2018-01-01",
  versiedatum: "2018-01-01",
  catalogus:
    "http://localhost:8003/catalogi/api/v1/catalogussen/ec77ad39-0954-4aeb-bcf2-6f45263cde77",
  besluittypen: [],
  gerelateerdeZaaktypen: [],
  url: "http://localhost:8003/catalogi/api/v1/zaaktypen/be210495-20b6-48ff-8d3d-3e44f74c43a4",
  identificatie: "ZAAKTYPE-2018-0000000001",
  omschrijvingGeneriek: "",
  toelichting: "",
  servicenorm: null,
  verlengingstermijn: null,
  trefwoorden: [],
  publicatietekst: "",
  verantwoordingsrelatie: [],
  selectielijstProcestype:
    "https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0",
  concept: false,
  broncatalogus: null,
  bronzaaktype: null,
  eindeGeldigheid: null,
  beginObject: "2018-01-01",
  eindeObject: null,
  statustypen: [
    "http://localhost:8003/catalogi/api/v1/statustypen/9438e56a-5d78-4dc8-9d9a-2404781f818d",
  ],
  resultaattypen: [
    "http://localhost:8003/catalogi/api/v1/resultaattypen/12903100-b7a0-4441-9645-eda7df2ad106",
  ],
  eigenschappen: [],
  informatieobjecttypen: [
    "http://localhost:8003/catalogi/api/v1/informatieobjecttypen/a8089bdf-72d3-414f-a9cd-953cfa602b6c",
  ],
  roltypen: [],
  deelzaaktypen: [],
  zaakobjecttypen: [],
};

export const FIXTURE_ZAAKTYPE_FIELDS: TypedField<
  components["schemas"]["ExpandableZaakType"]
>[] = [
  {
    name: "omschrijving",
    type: "string",
  },
  {
    name: "vertrouwelijkheidaanduiding",
    type: "string",
    options: [
      {
        label: "openbaar",
        value: "openbaar",
      },
      {
        label: "beperkt_openbaar",
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
        label: "zeer_geheim",
        value: "zeer_geheim",
      },
    ],
  },
  {
    name: "doel",
    type: "string",
  },
  {
    name: "aanleiding",
    type: "string",
  },
  {
    name: "indicatieInternOfExtern",
    type: "string",
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
  },
  {
    name: "handelingInitiator",
    type: "string",
  },
  {
    name: "onderwerp",
    type: "string",
  },
  {
    name: "handelingBehandelaar",
    type: "string",
  },
  {
    name: "doorlooptijd",
    type: "string",
  },
  {
    name: "opschortingEnAanhoudingMogelijk",
    type: "string",
  },
  {
    name: "verlengingMogelijk",
    type: "string",
  },
  {
    name: "publicatieIndicatie",
    type: "string",
  },
  {
    name: "productenOfDiensten",
    type: "string",
  },
  {
    name: "referentieproces",
    type: "string",
  },
  {
    name: "verantwoordelijke",
    type: "string",
  },
  {
    name: "beginGeldigheid",
    type: "string",
  },
  {
    name: "versiedatum",
    type: "string",
  },
  {
    name: "catalogus",
    type: "string",
  },
  {
    name: "besluittypen",
    type: "string",
  },
  {
    name: "gerelateerdeZaaktypen",
    type: "string",
  },
  {
    name: "url",
    type: "string",
  },
  {
    name: "identificatie",
    type: "string",
  },
  {
    name: "omschrijvingGeneriek",
    type: "string",
  },
  {
    name: "toelichting",
    type: "string",
  },
  {
    name: "servicenorm",
    type: "string",
  },
  {
    name: "verlengingstermijn",
    type: "string",
  },
  {
    name: "trefwoorden",
    type: "string",
  },
  {
    name: "publicatietekst",
    type: "string",
  },
  {
    name: "verantwoordingsrelatie",
    type: "string",
  },
  {
    name: "selectielijstProcestype",
    type: "string",
  },
  {
    name: "concept",
    type: "string",
  },
  {
    name: "broncatalogus",
    type: "string",
  },
  {
    name: "bronzaaktype",
    type: "string",
  },
  {
    name: "eindeGeldigheid",
    type: "string",
  },
  {
    name: "beginObject",
    type: "string",
  },
  {
    name: "eindeObject",
    type: "string",
  },
  {
    name: "statustypen",
    type: "string",
  },
  {
    name: "resultaattypen",
    type: "string",
  },
  {
    name: "eigenschappen",
    type: "string",
  },
  {
    name: "informatieobjecttypen",
    type: "string",
  },
  {
    name: "roltypen",
    type: "string",
  },
  {
    name: "deelzaaktypen",
    type: "string",
  },
  {
    name: "zaakobjecttypen",
    type: "string",
  },
];

export const FIXTURE_ZAAKTYPE_FIELDSETS: FieldSet<
  components["schemas"]["ExpandableZaakType"]
>[] = [
  [
    "Overview",
    {
      fields: [
        "identificatie",
        "omschrijving",
        "doel",
        "selectielijstProcestype",
      ],
    },
  ],
  [
    "General details",
    {
      fields: [
        "doel",
        "onderwerp",
        "aanleiding",
        "handelingInitiator",
        "handelingBehandelaar",
        "verantwoordelijke",
        "productenOfDiensten",
        "doorlooptijd",
        "servicenorm",
        "omschrijving",
        "omschrijvingGeneriek",
        "indicatieInternOfExtern",
        "vertrouwelijkheidaanduiding",
        "publicatieIndicatie",
        "publicatietekst",
        "selectielijstProcestype",
        "referentieproces",
        "identificatie",
        "gerelateerdeZaaktypen",
        "broncatalogus",
      ],
    },
  ],
];
export const FIXTURE_ZAAKTYPEN: components["schemas"]["ZaakTypeSummary"][] = [
  {
    url: "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/zaaktypen/3cec0e78-8840-4476-80d8-03fef41b9702",
    identificatie: "Zaaktype-0",
    omschrijving: "re-intermediate best-of-breed e-services",
    actief: true,
    eindeGeldigheid: null,
    vertrouwelijkheidaanduiding: "openbaar",
    versiedatum: "2025-06-27",
  },
  {
    url: "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/zaaktypen/004164e7-75ba-4d3c-b5ea-ec36593ab694",
    identificatie: "Zaaktype-999",
    omschrijving: "engage best-of-breed synergies",
    actief: true,
    eindeGeldigheid: null,
    vertrouwelijkheidaanduiding: "openbaar",
    versiedatum: "2018-01-01",
  },
  {
    url: "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/zaaktypen/87dd536a-ac75-4f67-9d11-ca20d7b37b18",
    identificatie: "Zaaktype-998",
    omschrijving: "envisioneer end-to-end systems",
    actief: true,
    eindeGeldigheid: null,
    vertrouwelijkheidaanduiding: "openbaar",
    versiedatum: "2018-01-01",
  },
];

export const FIXTURE_ZAAKTYPEN_FIELDS: TypedField<
  components["schemas"]["ZaakTypeSummary"]
>[] = [
  {
    name: "url",
    type: "string",
    filterLookup: "",
    options: [],
  },
  {
    name: "identificatie",
    type: "string",
    filterLookup: "identificatie",
    options: [],
  },
  {
    name: "omschrijving",
    type: "string",
    filterLookup: "",
    options: [],
  },
  {
    name: "actief",
    type: "boolean",
    filterLookup: "",
    options: [],
  },
  {
    name: "eindeGeldigheid",
    type: "string",
    filterLookup: "",
    options: [],
  },
  {
    name: "vertrouwelijkheidaanduiding",
    type: "string",
    filterLookup: "",
    options: [
      {
        label: "openbaar",
        value: "openbaar",
      },
      {
        label: "beperkt_openbaar",
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
        label: "zeer_geheim",
        value: "zeer_geheim",
      },
    ],
  },
  {
    name: "versiedatum",
    type: "string",
    filterLookup: "",
    options: [],
  },
];

export default FIXTURE_ZAAKTYPEN;

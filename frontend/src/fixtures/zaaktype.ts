import { FieldSet, TypedField } from "@maykin-ui/admin-ui";
import { components } from "~/types";

export const FIXTURE_ZAAKTYPE: components["schemas"]["ZaakType"] = {
  omschrijving: "engage best-of-breed synergies",
  vertrouwelijkheidaanduiding: "openbaar",
  doel: "Table hope production think fast here law soon. Energy our admit month either check very. Investment nothing property social rich low role number.",
  aanleiding:
    "Instead imagine federal cause wall sometimes. Game modern control bit shake. Can red full decade finish final rest.",
  indicatieInternOfExtern: "extern",
  handelingInitiator: "melden",
  onderwerp: "Klacht",
  handelingBehandelaar: "onderhouden",
  doorlooptijd: "P30D",
  opschortingEnAanhoudingMogelijk: false,
  verlengingMogelijk: false,
  publicatieIndicatie: true,
  productenOfDiensten: ["https://example.com/product/123"],
  referentieproces: {
    naam: "ReferentieProces 999",
    link: "",
  },
  verantwoordelijke: "100000999",
  beginGeldigheid: "2018-01-01",
  versiedatum: "2018-01-01",
  catalogus:
    "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/catalogussen/85028f4f-3d70-4ce9-8dbe-16a6b8613a54",
  besluittypen: [],
  gerelateerdeZaaktypen: [],
  url: "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/zaaktypen/004164e7-75ba-4d3c-b5ea-ec36593ab694",
  identificatie: "Zaaktype-999",
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
    "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/statustypen/a318ed24-80ad-4da0-b95f-69913aef994f",
    "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/statustypen/56df165f-c657-44b1-a498-ea440e749b05",
    "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/statustypen/03003779-800e-4951-844d-7478691cfd13",
  ],
  resultaattypen: [
    "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/resultaattypen/1ac42262-dbb8-49bd-a059-3e54752bdb74",
    "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/resultaattypen/4d453f16-04e7-4832-9e90-e59fda7e198d",
  ],
  eigenschappen: [
    "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/eigenschappen/8c5681f5-0c8b-44d5-a489-a0bad28ecf0c",
  ],
  informatieobjecttypen: [
    "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/informatieobjecttypen/09428c24-12e5-4c3a-a75c-e9e0d448a93b",
  ],
  roltypen: [
    "https://openzaak.test.maykin.opengem.nl/catalogi/api/v1/roltypen/10f1a5d8-d239-4e4f-8c9c-03c5d1e02027",
  ],
  deelzaaktypen: [],
  zaakobjecttypen: [],
};

export const FIXTURE_ZAAKTYPE_FIELDS: TypedField<
  components["schemas"]["ZaakType"]
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
  components["schemas"]["ZaakType"]
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

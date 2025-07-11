import { FieldSet, Outline } from "@maykin-ui/admin-ui";
import { NestedTabConfig, TargetType } from "~/pages";

export const FIELDSETS_ALGEMENE_INFORMATIE: FieldSet<TargetType>[] = [
  [
    "Algemeen",
    {
      titleSpan: 12,
      fields: ["identificatie"],
      span: 12,
      colSpan: 12,
    },
  ],

  [
    "",
    {
      fields: ["doel", "aanleiding", "toelichting", "omschrijvingGeneriek"],
      span: 12,
      colSpan: 6,
    },
  ],
  [
    "",
    {
      fields: [
        "vertrouwelijkheidaanduiding",
        "productenOfDiensten",
        "verantwoordingsrelatie",
      ],
      span: 12,
      colSpan: 4,
    },
  ],

  [
    "Geldigheid",
    {
      titleSpan: 12,
      fields: ["versiedatum", "beginGeldigheid", "eindeGeldigheid"],
      span: 12,
      colSpan: 4,
    },
  ],
];

export const FIELDSETS_BEHANDELING_EN_PROCES: FieldSet<TargetType>[] = [
  [
    "Referentieproces",
    {
      fields: ["referentieproces"], // TODO: Missing referentieprocesnaam & referentieproces url
      span: 12,
      colSpan: 6,
    },
  ],
  [
    "Behandeling",
    {
      fields: ["handelingInitiator", "handelingBehandelaar", "onderwerp"],
      span: 12,
      colSpan: 4,
    },
  ],
  [
    "",
    {
      fields: ["verantwoordelijke"],
      span: 12,
    },
  ],

  [
    "",
    {
      fields: ["doorlooptijd", "servicenorm"],
      span: 12,
      colSpan: 4,
    },
  ],

  [
    "Opschorten/verlengen",
    {
      titleSpan: 12,
      fields: [
        "opschortingEnAanhoudingMogelijk",
        "verlengingMogelijk",
        "verlengingstermijn",
      ],
      span: 12,
      colSpan: 4,
    },
  ],
];

export const FIELDSETS_BRONNEN_EN_RELATIES: FieldSet<TargetType>[] = [
  [
    "Brongegevens",
    {
      titleSpan: 12,
      fields: ["broncatalogus", "bronzaaktype"], // TODO: Missing broncatalogus domein, rsin, omschrijving, url, bronzaaktype omschijrving, bronzaaktype url
      span: 12,
      colSpan: 4,
    },
  ],

  [
    "Relaties",
    {
      titleSpan: 12,
      fields: ["catalogus", "deelzaaktypen", "gerelateerdeZaaktypen"],
      span: 12,
      colSpan: 4,
    },
  ],
  [
    "Gemeentelijke selectielijst",
    {
      titleSpan: 12,
      fields: [], // TODO: Missing "selectielijstconfiguratie resetten", "selectielijst procestype jaar", "selectielijst procestype"
      span: 12,
      colSpan: 4,
    },
  ],
];

export const FIELDSETS_PUBLICATIE: FieldSet<TargetType>[] = [
  [
    "Publicaties",
    {
      titleSpan: 12,
      fields: ["publicatieIndicatie"],
      span: 4,
    },
  ],
  [
    "",
    {
      fields: ["publicatietekst"],
      span: 8,
    },
  ],
];

export const TABS_CONFIG_ALGEMEEN: NestedTabConfig<TargetType> = {
  label: "Algemeen",
  tabs: [
    {
      view: "AttributeGrid",
      label: "Algemeen",
      icon: <Outline.DocumentIcon />,
      allowedFields: ["naam", "omschrijving"],
      fieldsets: FIELDSETS_ALGEMENE_INFORMATIE,
    },
    {
      view: "AttributeGrid",
      label: "Behandeling en proces",
      icon: <Outline.ArrowPathIcon />,
      allowedFields: ["naam", "omschrijving"],
      fieldsets: FIELDSETS_BEHANDELING_EN_PROCES,
    },
    {
      view: "AttributeGrid",
      label: "Bronnen en relaties",
      icon: <Outline.LinkIcon />,
      allowedFields: ["naam", "omschrijving"],
      fieldsets: FIELDSETS_BRONNEN_EN_RELATIES,
    },
    {
      view: "AttributeGrid",
      label: "Publicatie",
      icon: <Outline.ArchiveBoxIcon />,
      allowedFields: ["naam", "omschrijving"],
      fieldsets: FIELDSETS_PUBLICATIE,
    },
  ],
};

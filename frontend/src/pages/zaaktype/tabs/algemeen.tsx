import { FieldSet, Outline } from "@maykin-ui/admin-ui";
import { TabConfig, TargetType } from "~/pages";

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

export const TABS_CONFIG_ALGEMEEN: TabConfig<TargetType> = {
  label: "Algemeen",
  view: "AttributeGrid",
  sections: [
    {
      label: "Algemeen",
      icon: <Outline.DocumentIcon />,
      expandFields: ["naam", "omschrijving"],
      fieldsets: FIELDSETS_ALGEMENE_INFORMATIE,
    },
    {
      label: "Behandeling en proces",
      icon: <Outline.ArrowPathIcon />,
      expandFields: ["naam", "omschrijving"],
      fieldsets: FIELDSETS_BEHANDELING_EN_PROCES,
    },
    {
      label: "Bronnen en relaties",
      icon: <Outline.LinkIcon />,
      expandFields: ["naam", "omschrijving"],
      fieldsets: FIELDSETS_BRONNEN_EN_RELATIES,
    },
    {
      label: "Publicatie",
      icon: <Outline.ArchiveBoxIcon />,
      expandFields: ["naam", "omschrijving"],
      fieldsets: FIELDSETS_PUBLICATIE,
    },
  ],
};

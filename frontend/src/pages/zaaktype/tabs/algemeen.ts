import { FieldSet } from "@maykin-ui/admin-ui";
import { TabConfig, TargetType } from "~/pages";

export const FIELDSETS_ALGEMEEN: FieldSet<TargetType>[] = [
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

  // TODO: Should be "Behandeling" section
  [
    "",
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

export const TAB_CONFIG_ALGEMEEN: TabConfig<TargetType> = {
  allowedFields: ["naam", "omschrijving"],
  label: "Algemeen",
  view: "AttributeGrid",
  fieldsets: FIELDSETS_ALGEMEEN,
};

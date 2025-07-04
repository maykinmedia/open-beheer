import { FieldSet } from "@maykin-ui/admin-ui";
import { ZaaktypeLoaderData } from "~/pages";
import { components } from "~/types";

type ExpandFieldConfig =
  | { type: "priority"; keys: string[] } // TODO: keyof Zaaktype[] but currently doesn't work, explore why
  | { type: "object"; keys: string[] };

type ExpandableKeys = keyof ZaaktypeLoaderData["result"]["_expand"];

const TABS_CONFIG: Record<
  "Overzicht" | "Statustypen",
  Partial<Record<ExpandableKeys, ExpandFieldConfig>>
> = {
  Overzicht: {
    statustypen: { type: "priority", keys: ["omschrijving", "statustype"] },
    informatieobjecttypen: { type: "priority", keys: ["omschrijving", "naam"] },
    roltypen: { type: "priority", keys: ["omschrijving", "naam"] },
    resultaattypen: { type: "priority", keys: ["omschrijving", "naam"] },
    eigenschappen: { type: "priority", keys: ["omschrijving", "naam"] },
    zaakobjecttypen: { type: "priority", keys: ["omschrijving", "naam"] },
    besluittypen: { type: "priority", keys: ["omschrijving", "naam"] },
  },
  Statustypen: {
    statustypen: {
      type: "object",
      keys: ["omschrijving", "volgnummer"],
    },
  },
};

const FIELDSETS_OVERVIEW: FieldSet<components["schemas"]["ZaakType"]>[] = [
  [
    "",
    {
      fields: ["identificatie"],
      span: 4,
    },
  ],
  [
    "",
    {
      fields: ["omschrijving"],
      span: 8,
    },
  ],
  [
    "",
    {
      fields: ["doel"],
      span: 12,
    },
  ],
  [
    "",
    {
      fields: ["statustypen", "informatieobjecttypen", "roltypen"],
      span: 4,
    },
  ],
  [
    "",
    {
      fields: ["resultaattypen", "eigenschappen", "gerelateerdeZaaktypen"],
      span: 4,
    },
  ],
  [
    "",
    {
      fields: ["zaakobjecttypen", "selectielijstProcestype"],
      span: 4,
    },
  ],
];

const FIELDSETS_GENERAL: FieldSet<components["schemas"]["ZaakType"]>[] = [
  [
    "Algemeen",
    {
      fields: ["omschrijving", "aanleiding"],
      span: 6,
    },
  ],
  [
    "",
    {
      fields: ["omschrijvingGeneriek"],
      span: 6,
    },
  ],
  [
    "",
    {
      fields: ["doel"],
      span: 6,
    },
  ],
  [
    "",
    {
      fields: ["toelichting"],
      span: 6,
    },
  ],
  [
    "",
    {
      fields: ["vertrouwelijkheidaanduiding"],
      span: 4,
    },
  ],
  [
    "",
    {
      fields: ["productenOfDiensten"],
      span: 4,
    },
  ],
  [
    "",
    {
      fields: ["verantwoordingsrelatie"],
      span: 4,
    },
  ],
  // [
  //   "",
  //   {
  //     fields: ["uuid"],
  //     span: 4,
  //   },
  // ],
  [
    "",
    {
      fields: ["identificatie"],
      span: 12,
    },
  ],
  [
    "Geldigheid",
    {
      fields: ["versiedatum"],
      span: 4,
    },
  ],
  [
    "",
    {
      fields: ["beginGeldigheid"],
      span: 4,
    },
  ],
  [
    "",
    {
      fields: ["eindeGeldigheid"],
      span: 4,
    },
  ],
];

export type { ExpandFieldConfig };
export { TABS_CONFIG, FIELDSETS_GENERAL, FIELDSETS_OVERVIEW };

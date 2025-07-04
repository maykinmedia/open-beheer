import { FieldSet } from "@maykin-ui/admin-ui";
import { TabConfig, TargetType } from "~/pages";

export const FIELDSETS_OVERVIEW: FieldSet<TargetType>[] = [
  [
    "",
    {
      fields: ["identificatie", "omschrijving"],
      span: 12,
      colSpan: 6,
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
      fields: [
        "statustypen",
        "informatieobjecttypen",
        "resultaattypen",
        "eigenschappen",
        "zaakobjecttypen",
        "selectielijstProcestype",
      ],
      span: 12,
      colSpan: 6,
    },
  ],
];

export const TAB_CONFIG_OVERVIEW: TabConfig<TargetType> = {
  allowedFields: ["naam", "omschrijving"],
  label: "Overzicht",
  view: "AttributeGrid",
  fieldsets: FIELDSETS_OVERVIEW,
};

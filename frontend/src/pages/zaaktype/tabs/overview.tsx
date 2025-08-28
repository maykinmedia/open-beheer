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

export const TABS_CONFIG_OVERVIEW: TabConfig<TargetType> = {
  label: "Overzicht",
  view: "AttributeGrid",
  sections: [
    {
      expandFields: ["procestype", "naam", "omschrijving"],
      label: "Overzicht",
      fieldsets: FIELDSETS_OVERVIEW,
      valueTransform: {
        selectielijstProcestype: (record) => {
          return {
            ...record,
            procestype: `${record.naam} - ${record.jaar}`,
          };
        },
      },
    },
  ],
};

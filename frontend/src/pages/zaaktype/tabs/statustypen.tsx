import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_STATUSTYPEN: TabConfig<TargetType> = {
  label: "Statustypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        { name: "volgnummer", type: "number" },
        "omschrijving",
        "omschrijvingGeneriek",
        { name: "informeren", type: "boolean" },
      ],
      label: "Statustypen",
      key: "statustypen",
    },
  ],
};

import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_RESULTAATTYPEN: TabConfig<TargetType> = {
  label: "Resultaattypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        "resultaattypenOmschrijving",
        "resultaattypeomschrijving",
        "selectielijstklasse",
        "url",
      ], // TODO: Missing "uuid"
      label: "Resultaattypen",
      key: "resultaattypen",
    },
  ],
};

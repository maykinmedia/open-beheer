import { NestedTabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_RESULTAATTYPEN: NestedTabConfig<TargetType> = {
  label: "Resultaattypen",
  tabs: [
    {
      allowedFields: [
        "resultaattypenOmschrijving",
        "resultaattypeomschrijving",
        "selectielijstklasse",
        "url",
      ], // TODO: Missing "uuid"
      label: "Resultaattypen",
      key: "resultaattypen",
      view: "DataGrid",
    },
  ],
};

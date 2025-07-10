import { TabConfig, TargetType } from "~/pages";

export const TAB_CONFIG_RESULTAATTYPEN: TabConfig<TargetType> = {
  allowedFields: [
    "resultaattypenOmschrijving",
    "resultaattypeomschrijving",
    "selectielijstklasse",
    "url",
  ], // TODO: Missing "uuid"
  label: "Resultaattypen",
  key: "resultaattypen",
  view: "DataGrid",
};

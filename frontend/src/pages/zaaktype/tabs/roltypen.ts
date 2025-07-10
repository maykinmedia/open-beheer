import { TabConfig, TargetType } from "~/pages";

export const TAB_CONFIG_ROLTYPEN: TabConfig<TargetType> = {
  allowedFields: [
    // TODO: Missing "Roltypen", "Roltypen Omschrijving", "Roltypen UUID"
  ],
  label: "Roltypen",
  key: "roltypen",
  view: "DataGrid",
};

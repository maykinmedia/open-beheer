import { TabConfig, TargetType } from "~/pages";

export const TAB_CONFIG_STATUSTYPEN: TabConfig<TargetType> = {
  allowedFields: ["volgnummer", "omschrijving"],
  label: "Statustypen",
  key: "statustypen",
  view: "DataGrid",
};

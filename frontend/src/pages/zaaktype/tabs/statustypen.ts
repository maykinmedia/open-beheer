import { TabConfig, TargetType } from "~/pages";

export const TAB_CONFIG_STATUSTYPEN: TabConfig<TargetType> = {
  allowedFields: ["volgnummer", "statustype", "url"], // TODO: Should be uuid instead of URL
  label: "Statustypen",
  key: "statustypen",
  view: "DataGrid",
};

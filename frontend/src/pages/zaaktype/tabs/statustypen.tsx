import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_STATUSTYPEN: TabConfig<TargetType> = {
  label: "Statustypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: ["volgnummer", "statustype", "url"], // TODO: Should be uuid instead of URL
      label: "Statustypen",
      key: "statustypen",
    },
  ],
};

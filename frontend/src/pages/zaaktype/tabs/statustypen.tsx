import { NestedTabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_STATUSTYPEN: NestedTabConfig<TargetType> = {
  label: "Statustypen",
  tabs: [
    {
      allowedFields: ["volgnummer", "statustype", "url"], // TODO: Should be uuid instead of URL
      label: "Statustypen",
      key: "statustypen",
      view: "DataGrid",
    },
  ],
};

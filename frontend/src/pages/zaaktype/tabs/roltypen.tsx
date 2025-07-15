import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_ROLTYPEN: TabConfig<TargetType> = {
  label: "Roltypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        // TODO: Missing "Roltypen", "Roltypen Omschrijving", "Roltypen UUID"
      ],
      label: "Roltypen",
      key: "roltypen",
    },
  ],
};

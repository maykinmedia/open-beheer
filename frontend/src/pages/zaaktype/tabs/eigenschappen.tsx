import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_EIGENSCHAPPEN: TabConfig<TargetType> = {
  label: "Eigenschappen",
  view: "DataGrid",
  sections: [
    {
      // TODO: Not implemented
      expandFields: [],
      label: "Eigenschappen",
      key: "eigenschappen",
    },
  ],
};

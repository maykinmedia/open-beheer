import { NestedTabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_EIGENSCHAPPEN: NestedTabConfig<TargetType> = {
  label: "Eigenschappen",
  tabs: [
    {
      // TODO: Not implemented
      allowedFields: [],
      label: "Eigenschappen",
      key: "eigenschappen",
      view: "DataGrid",
    },
  ],
};

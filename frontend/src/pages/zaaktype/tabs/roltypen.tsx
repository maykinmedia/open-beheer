import { NestedTabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_ROLTYPEN: NestedTabConfig<TargetType> = {
  label: "Roltypen",
  tabs: [
    {
      allowedFields: [
        // TODO: Missing "Roltypen", "Roltypen Omschrijving", "Roltypen UUID"
      ],
      label: "Roltypen",
      key: "roltypen",
      view: "DataGrid",
    },
  ],
};

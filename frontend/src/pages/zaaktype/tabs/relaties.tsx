import { NestedTabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_RELATIES: NestedTabConfig<TargetType> = {
  label: "Relaties",
  tabs: [
    {
      allowedFields: ["relatieOmschrijving"],
      label: "Relaties",
      key: "roltypen", // TODO: Missing "Relaties" key
      view: "DataGrid",
    },
  ],
};

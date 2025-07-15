import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_RELATIES: TabConfig<TargetType> = {
  label: "Relaties",
  view: "DataGrid",
  sections: [
    {
      expandFields: ["relatieOmschrijving"],
      label: "Relaties",
      key: "roltypen", // TODO: Missing "Relaties" key
    },
  ],
};

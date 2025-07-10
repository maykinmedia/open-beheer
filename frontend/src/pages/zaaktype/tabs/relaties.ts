import { TabConfig, TargetType } from "~/pages";

export const TAB_CONFIG_RELATIES: TabConfig<TargetType> = {
  allowedFields: ["relatieOmschrijving"],
  label: "Relaties",
  key: "roltypen", // TODO: Missing "Relaties" key
  view: "DataGrid",
};

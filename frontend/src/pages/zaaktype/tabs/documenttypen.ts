import { TabConfig, TargetType } from "~/pages";

export const TAB_CONFIG_DOCUMENTTYPEN: TabConfig<TargetType> = {
  allowedFields: [
    // TODO: Missing design
  ],
  label: "Documenttypen",
  key: "zaakobjecttypen", // TODO: Missing "documenttypen" key
  view: "DataGrid",
};

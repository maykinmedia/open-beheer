import { NestedTabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_DOCUMENTTYPEN: NestedTabConfig<TargetType> = {
  label: "Documenttypen",
  tabs: [
    {
      allowedFields: [
        // TODO: Missing design
      ],
      label: "Documenttypen",
      key: "zaakobjecttypen", // TODO: Missing "documenttypen" key
      view: "DataGrid",
    },
  ],
};

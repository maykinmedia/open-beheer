import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_DOCUMENTTYPEN: TabConfig<TargetType> = {
  label: "Documenttypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        // TODO: Missing design
      ],
      label: "Documenttypen",
      key: "zaakobjecttypen", // TODO: Missing "documenttypen" key
    },
  ],
};

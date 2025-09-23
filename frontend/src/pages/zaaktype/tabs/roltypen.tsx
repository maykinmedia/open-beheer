import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_ROLTYPEN: TabConfig<TargetType> = {
  label: "Roltypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        "_expand.roltypen.omschrijving",
        "_expand.roltypen.omschrijvingGeneriek",
      ],
      label: "Roltypen",
      key: "roltypen",
    },
  ],
};

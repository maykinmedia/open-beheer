import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_RELATIES: TabConfig<TargetType> = {
  label: "Relaties",
  view: "DataGrid",
  sections: [
    {
      expandFields: ["_expand.deelzaaktypen.omschrijvingGeneriek"],
      label: "Relaties",
      key: "deelzaaktypen",
    },
  ],
};

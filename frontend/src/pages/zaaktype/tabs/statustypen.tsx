import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_STATUSTYPEN: TabConfig<TargetType> = {
  label: "Statustypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        "_expand.statustypen.volgnummer",
        "_expand.statustypen.omschrijving",
        "_expand.statustypen.omschrijvingGeneriek",
        "_expand.statustypen.informeren",
      ],
      label: "Statustypen",
      key: "statustypen",
    },
  ],
};

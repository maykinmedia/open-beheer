import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_ZAAKTYPE_INFORMATIEOBJECTTYPEN: TabConfig<TargetType> =
  {
    label: "Zaaktype-Informatieobjecttypen",
    view: "DataGrid",
    sections: [
      {
        expandFields: [
          "_expand.zaaktypeInformatieobjecttypen.volgnummer",
          "_expand.zaaktypeInformatieobjecttypen.informatieobjecttype",
          "_expand.zaaktypeInformatieobjecttypen.richting",
        ],
        label: "Zaaktype-Informatieobjecttypen",
        key: "zaaktypeInformatieobjecttypen",
      },
    ],
  };

import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_OBJECTTYPEN: TabConfig<TargetType> = {
  label: "Zaakobjecttypen",
  view: "DataGrid",
  sections: [
    {
      key: "zaakobjecttypen",
      label: "Zaakobjecttypen",
      expandFields: [
        "_expand.zaakobjecttypen.objecttype",
        "_expand.zaakobjecttypen.anderObjecttype",
        "_expand.zaakobjecttypen.relatieOmschrijving",
      ],
    },
  ],
};

import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_OBJECTTYPEN: TabConfig<TargetType> = {
  label: "Objecttypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        "objecttype",
        "anderObjecttype",
        "beginObject",
        "eindeObject",
      ],
      label: "Objecttypen",
      key: "zaakobjecttypen",
    },
  ],
};

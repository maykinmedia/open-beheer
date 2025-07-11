import { NestedTabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_OBJECTTYPEN: NestedTabConfig<TargetType> = {
  label: "Objecttypen",
  tabs: [
    {
      allowedFields: [
        "objecttype",
        "anderObjecttype",
        "beginObject",
        "eindeObject",
      ],
      label: "Objecttypen",
      key: "zaakobjecttypen",
      view: "DataGrid",
    },
  ],
};

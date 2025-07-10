import { TabConfig, TargetType } from "~/pages";

export const TAB_CONFIG_OBJECTTYPEN: TabConfig<TargetType> = {
  allowedFields: [
    "objecttype",
    "anderObjecttype",
    "beginObject",
    "eindeObject",
  ],
  label: "Objecttypen",
  key: "zaakobjecttypen",
  view: "DataGrid",
};

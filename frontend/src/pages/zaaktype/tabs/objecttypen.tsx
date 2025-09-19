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
      valueTransform: {
        zaakobjecttypen: (zaakobjecttypen) => {
          return (zaakobjecttypen || []).map((item) => {
            return {
              ...item,
              objecttype: item ? `${item._expand.objecttype?.name}` : "-",
            };
          });
        },
      },
    },
  ],
};

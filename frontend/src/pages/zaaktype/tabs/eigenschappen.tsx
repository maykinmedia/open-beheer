import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_EIGENSCHAPPEN: TabConfig<TargetType> = {
  label: "Eigenschappen",
  view: "DataGrid",
  sections: [
    {
      // TODO: Not implemented
      expandFields: [
        "naam",
        "definitie",
        {
          name: "specificatie",
          type: "string",
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: (value) => {
            if (typeof value === "undefined") {
              return {
                formaat: "tekst",
                lengte: "255",
                kardinaliteit: "1",
              };
            }
          },
          valueTransform: (value) => {
            return JSON.stringify(value.specificatie);
          },
        },
      ],
      label: "Eigenschappen",
      key: "eigenschappen",
    },
  ],
};

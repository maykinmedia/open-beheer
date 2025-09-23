import { TabConfig, TargetType } from "~/pages";
import { components } from "~/types";

export const TABS_CONFIG_EIGENSCHAPPEN: TabConfig<TargetType> = {
  label: "Eigenschappen",
  view: "DataGrid",
  sections: [
    {
      // TODO: Not implemented
      expandFields: [
        "_expand.eigenschappen.naam",
        "_expand.eigenschappen.definitie",
        {
          name: "_expand.eigenschappen.specificatie",
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
          valueTransform: (
            value: components["schemas"]["Eigenschap"],
          ): string => {
            return JSON.stringify(value.specificatie);
          },
        },
      ],
      label: "Eigenschappen",
      key: "eigenschappen",
    },
  ],
};

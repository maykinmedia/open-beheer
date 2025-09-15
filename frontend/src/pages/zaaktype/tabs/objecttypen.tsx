import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_OBJECTTYPEN: TabConfig<TargetType> = {
  label: "Objecttypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        "objecttype",
        {
          name: "anderObjecttype",
          type: "boolean",
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: () => false,
        },
        {
          name: "beginGeldigheid",
          type: "string", // FIXME: if we use date, the value is not turned into a YYYY-MM-DD format
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: () => {
            const today = new Date();
            return today.toISOString().split("T")[0];
          },
        },
        {
          name: "eindeGeldigheid",
          type: "string", // FIXME: if we use date, the value is not turned into a YYYY-MM-DD format
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: () => {
            const today = new Date();
            today.setFullYear(today.getFullYear() + 1);
            return today.toISOString().split("T")[0];
          },
        },
        {
          name: "relatieOmschrijving",
          type: "string",
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: () => {
            return "Object relation";
          },
        },
      ],
      label: "Objecttypen",
      key: "zaakobjecttypen",
    },
  ],
};

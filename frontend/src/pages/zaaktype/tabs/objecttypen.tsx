import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_OBJECTTYPEN: TabConfig<TargetType> = {
  label: "Objecttypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        {
          name: "objecttype",
          type: "string",
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: () => undefined,
        },
        {
          name: "anderObjecttype",
          type: "boolean",
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: () => undefined,
        },
        {
          name: "beginGeldigheid",
          type: "string", // FIXME: if we use date, the value is not turned into a YYYY-MM-DD format
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: () => undefined,
        },
        {
          name: "eindeGeldigheid",
          type: "string", // FIXME: if we use date, the value is not turned into a YYYY-MM-DD format
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: () => undefined,
        },
        {
          name: "relatieOmschrijving",
          type: "string",
          // @ts-expect-error - FIXME: Extending TypedField here.
          initValue: () => undefined,
        },
      ],
      label: "Objecttypen",
      key: "zaakobjecttypen",
    },
  ],
};

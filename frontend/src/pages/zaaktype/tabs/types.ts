import { FieldSet } from "@maykin-ui/admin-ui";
import { ReactNode } from "react";
import { ZaaktypeLoaderData } from "~/pages";
import { Expand, ExpandItemKeys, Expanded } from "~/types";

/**
 * `TargetType`:
 * Alias for the primary result object returned by the ZaaktypeLoaderData.
 * This is the base type used when referencing the data rendered inside a tab.
 */
export type TargetType = ZaaktypeLoaderData["result"];

/**
 * The type a the primary tab.
 */
export type TabConfig<T extends object> =
  | {
      label: string;
      view: "AttributeGrid";
      sections: AttributeGridSection<T>[];
    }
  | {
      label: string;
      view: "DataGrid";
      sections: DataGridSection<Expanded<T>>[];
    };

export type BaseTabSection<T extends object> = {
  expandFields: ExpandItemKeys<T>[];
  icon?: ReactNode;
  label: string;
  valueTransform?: Partial<{
    [K in keyof Expand<T>]: (
      record: NonNullable<Expand<T>[K]>,
    ) => WithTransform<NonNullable<Expand<T>[K]>>;
  }>;
};
type WithTransform<T> = T extends (infer U)[]
  ? (U & { transform: ReactNode })[] // array of objects, each has transform
  : T & { transform: ReactNode }; // single object, add transform

export type AttributeGridSection<T extends object> = BaseTabSection<T> & {
  fieldsets: FieldSet<Expanded<T>>[];
};

export type DataGridSection<T extends object> = BaseTabSection<T> & {
  key: keyof Expand<Expanded<T>>;
};

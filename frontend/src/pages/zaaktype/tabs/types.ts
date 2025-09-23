import { FieldSet, TypedField } from "@maykin-ui/admin-ui";
import { ReactNode } from "react";
import { ZaaktypeLoaderData } from "~/pages";
import {
  Expand,
  ExpandItemKeys,
  Expanded,
  RelatedObject,
  components,
} from "~/types";

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

type ExpandItemKeysWithString<T> = ExpandItemKeys<T> | string;

export type BaseTabSection<
  T extends object,
  R extends RelatedObject<T> = RelatedObject<T>,
> = {
  expandFields: (
    | ExpandItemKeysWithString<T>
    | TypedField<R>
    | components["schemas"]["OBField"]
  )[];
  icon?: ReactNode;
  label: string;
  valueTransform?: Partial<{
    [K in keyof Expand<T>]: (
      value: Expand<T>[K],
    ) => Record<string, unknown> | Record<string, unknown>[];
  }>;
};
export type AttributeGridSection<T extends object> = BaseTabSection<T> & {
  fieldsets: FieldSet<Expanded<T>>[];
};

export type DataGridSection<T extends object> = BaseTabSection<T> & {
  key: keyof Expand<Expanded<T>>;
};

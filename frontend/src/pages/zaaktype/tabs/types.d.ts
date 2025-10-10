import { Field, FieldSet, TypedField } from "@maykin-ui/admin-ui";
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
  | AttributeGridTabConfig<T>
  | DataGridTabConfig<T>;

type BaseTabConfig = {
  label: string;
};

export type AttributeGridTabConfig<T extends object> = BaseTabConfig & {
  key: string;
  view: "AttributeGrid";
  sections: AttributeGridSection<T>[];
};

export type DataGridTabConfig<T extends object> = BaseTabConfig & {
  key: keyof Expand<Expanded<T>>;
  view: "DataGrid";
  fieldset: FieldSet;
  sections: DataGridSection<Expanded<T>>[];
};

type ExpandItemKeysWithString<T> = ExpandItemKeys<T> | string;

type BaseTabSection<
  T extends object,
  R extends RelatedObject<T> = RelatedObject<T>,
> = {
  expandFields: (Field<R> | TypedField<R> | components["schemas"]["OBField"])[];
  icon?: ReactNode;
  label: string;
  valueTransform?: Partial<{
    [K in keyof Expand<T>]: (
      value: Expand<T>[K],
    ) => Record<string, unknown> | Record<string, unknown>[];
  }>;
};
export type AttributeGridSection<T extends object> = BaseTabSection<T> & {
  fieldsets: FieldSet<T>[];
};

export type DataGridSection<T extends object> = BaseTabSection<T> & {
  key: keyof Expand<Expanded<T>>;
};

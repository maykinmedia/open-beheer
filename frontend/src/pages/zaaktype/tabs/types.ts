import { FieldSet } from "@maykin-ui/admin-ui";
import { ReactNode } from "react";
import { ZaaktypeLoaderData } from "~/pages";

/**
 * `TargetType`:
 * Alias for the primary result object returned by the ZaaktypeLoaderData.
 * This is the base type used when referencing the data rendered inside a tab.
 */
export type TargetType = ZaaktypeLoaderData["result"];

/**
 * `Expand`:
 * Extracts the non-nullable `_expand` field from the `TargetType`.
 * `_expand` contains related resources (e.g., statustypen, resultaattypen)
 * which are rendered differently depending on the tab.
 */
export type Expand = NonNullable<TargetType["_expand"]>;

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
      sections: DataGridSection[];
    };

export type BaseTabSection = {
  expandFields: ExpandItemKeys[];
  icon?: ReactNode;
  label: string;
};

export type AttributeGridSection<T extends object> = BaseTabSection & {
  fieldsets: FieldSet<T>[];
};

export type DataGridSection = BaseTabSection & {
  key: keyof TargetType["_expand"];
};

/**
 * `ExpandItemKeys`:
 * A union of all possible field names across all related resource types in `_expand`.
 *
 * For example, if `_expand` looks like:
 * ```ts
 * {
 *   statustypen?: StatusType[];
 *   resultaattypen?: ResultaatType[];
 * }
 * ```
 * Then this type will evaluate to:
 * ```ts
 * keyof (StatusType | ResultaatType)
 * ```
 *
 * This enables strongly typed `allowedFields` even when accessing dynamic or nested data.
 */
export type ExpandItemKeys = NonNullable<
  {
    [K in keyof Expand]: Expand[K] extends (infer U)[] | undefined
      ? keyof U
      : never;
  }[keyof Expand]
>;

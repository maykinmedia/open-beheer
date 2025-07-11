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
 * `LeafTabConfig<T>` is a discriminated union that describes a single tab in a tabbed interface.
 *
 * Each tab can render one of the following views:
 * - `"AttributeGrid"`: Displays fields from a single object, grouped into fieldsets.
 * - `"DataGrid"`: Displays related objects from the `_expand` section of the main object.
 *
 * ## Common properties
 * - `allowedFields`: List of field names allowed to be displayed in this tab.
 * - `icon`: Optional icon to render alongside the label.
 * - `label`: Label shown in the tab header.
 *
 * ## When `view: "AttributeGrid"`
 * - `allowedFields`: For the properties containing a related _expand_ object, this specifies what property of those it takes as a replacement (by priority).
 * - `fieldsets`: Defines how fields are grouped for rendering in the `AttributeGrid`.
 *
 * ## When `view: "DataGrid"`
 * - `allowedFields`: Specifies which fields from the related objects can be displayed in the grid.
 * - `fieldsets`: Must be omitted.
 * - `key`: Specifies which property of the `_expand` object to use as data source.
 */
export type LeafTabConfig<T extends object> =
  | {
      view: "AttributeGrid";
      allowedFields: ExpandItemKeys[];
      fieldsets: FieldSet<T>[];
      icon?: ReactNode;
      label: string;
    }
  | {
      view: "DataGrid";
      allowedFields: ExpandItemKeys[];
      fieldsets?: never;
      icon?: ReactNode;
      key: keyof TargetType["_expand"];
      label: string;
    };

/**
 * `NestedTabConfig<T>` defines the structure for a tabbed UI layout.
 * Each tab is configured using a `LeafTabConfig`.
 */
export type NestedTabConfig<T extends object> = {
  label: string;
  tabs: LeafTabConfig<T>[];
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
 * keyof StatusType | keyof ResultaatType
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

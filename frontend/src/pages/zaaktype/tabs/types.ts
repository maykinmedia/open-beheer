import { FieldSet } from "@maykin-ui/admin-ui";
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
 * `TabConfig<T>`:
 * A union type representing a configuration for a single tab inside a tabbed view.
 *
 * Tabs can either:
 * - Show attributes of a single object (`view: "attribute"`)
 * - Show related data in tabular form (`view: "data"`)
 *
 * ### Shared fields:
 * - `label`: The visible label of the tab.
 * - `allowedFields`: The subset of fields allowed to be rendered in the tab. Can be:
 *   - Fields from the main object (`ZaaktypeLoaderData["result"]`)
 *
 * ### For `view: "attribute"`:
 * - `fieldsets`: Defines how the fields are grouped when rendered in an AttributeGrid.
 *
 * ### For `view: "data"`:
 * - `key`: The property of `_expand` whose list of related objects will be rendered in a DataGrid.
 */
export type TabConfig<T extends object> =
  | {
      view: "AttributeGrid";
      label: string;
      allowedFields: ExpandItemKeys[];
      fieldsets: FieldSet<T>[];
    }
  | {
      view: "DataGrid";
      label: string;
      key: keyof TargetType["_expand"];
      allowedFields: ExpandItemKeys[];
      fieldsets?: never;
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

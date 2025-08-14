/**
 * `Expanded`
 * A value with an _expand field.
 */
export type Expanded<T extends object> = T extends {
  _expand: Record<string, object | object[]>;
}
  ? T
  : never;

/**
 * `Expand`:
 * Extracts the non-nullable `_expand` field from `T`.
 * `_expand` contains related resources (e.g., statustypen, resultaattypen)
 */
export type Expand<T extends object> =
  T extends Expanded<T> ? NonNullable<T["_expand"]> : never;

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
export type ExpandItemKeys<T extends Expanded> = NonNullable<
  {
    [K in keyof Expand<T>]: Expand<T>[K] extends (infer U)[] | undefined
      ? keyof U
      : never;
  }[keyof Expand<T>]
>;

/**
 * Extracts the item type for a specific field in the `_expand` map.
 *
 * Example:
 * RelatedObject<MyObject> = StatusType
 */
export type RelatedObject<T extends object> =
  NonNullable<Expand<T>[keyof Expand<T>]> extends (infer U)[]
    ? U extends object
      ? U
      : never
    : never;

// export type RelatedObject<T extends object> = Expand<T>[keyof Expand<T>];

import { Badge } from "@maykin-ui/admin-ui";
import { isPrimitive } from "~/lib";
import { ExpandItemKeys, RelatedObject } from "~/types";

type RelatedObjectBadgeProps<T extends object> = {
  relatedObject: RelatedObject<T>;
  allowedFields: ExpandItemKeys<T>[];
};

/**
 * Finds the first primitive field in `relatedObject` that is allowed,
 * then displays its value inside a Badge. Throws if no allowed key is found.
 *
 * @param relatedObject - Single related resource relatedObject
 * @param allowedFields - List of field names permitted for display
 * @returns A Badge containing the primitive value, or null for non-primitives
 * @throws InvalidRelatedObjectError When no allowed key exists
 */
export function RelatedObjectBadge<T extends object>({
  relatedObject,
  allowedFields,
}: RelatedObjectBadgeProps<T>) {
  const key = allowedFields.find((k) => Object.keys(relatedObject).includes(k));
  if (!key) return null;

  // Extract value.
  const value = relatedObject[key];
  return isPrimitive(value) ? <Badge>{value}</Badge> : null;
}

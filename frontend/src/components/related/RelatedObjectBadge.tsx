import { Badge, Primitive } from "@maykin-ui/admin-ui";
import { isPrimitive } from "~/lib";
import { ExpandItemKeys } from "~/types";

type RelatedObjectBadgeProps<T extends object> = {
  relatedObject: Record<ExpandItemKeys<T>, Primitive | object>;
  allowedFields: ExpandItemKeys<T>[];
};

/**
 * Finds the first primitive field in `relatedObject` that is allowed,
 * then displays its value inside a Badge. Throws if no allowed key is found.
 *
 * @param relatedObject - Single related resource object
 * @param allowedFields - List of field names permitted for display
 * @returns A Badge containing the primitive value, or null for non-primitives
 * @throws InvalidRelatedObjectError When no allowed key exists
 */
export function RelatedObjectBadge<T extends object>({
  relatedObject,
  allowedFields,
}: RelatedObjectBadgeProps<T>) {
  const objectKeys = Object.keys(
    relatedObject,
  ) as (keyof typeof relatedObject)[];

  const key = objectKeys.find((k) => allowedFields.includes(k));
  // Bail early, no renderable data.
  if (!key) {
    throw new InvalidRelatedObjectError({
      object: relatedObject,
      allowedFields,
    });
  }

  // Extract value.
  const value = relatedObject[key];
  return isPrimitive(value) ? <Badge>{value}</Badge> : null;
}

export class InvalidRelatedObjectError extends Error {
  constructor(data: unknown) {
    const baseMessage =
      "<RelatedObjectList /> received an invalid related object";
    const detail =
      data && typeof data === "object"
        ? `: ${JSON.stringify(data, null, 2)}`
        : "";

    super(`${baseMessage}${detail}`);
    this.name = "InvalidRelatedObjectError";
  }
}

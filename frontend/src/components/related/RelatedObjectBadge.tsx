import { A, Badge, Outline } from "@maykin-ui/admin-ui";
import { NavLink } from "react-router";
import { isPrimitive } from "~/lib";

import "./RelatedObjectBadge.css";

/**
 * This refers to the fields in an object which are allowed to be rendered for
 * an related object. If none of those match: an attempt may be made to automatically
 * find candidates.
 */
export const DEFAULT_ALLOWED_FIELDS = [
  "procestype",
  "naam",
  "omschrijving",
  "objecttype",
];

type RelatedObjectBadgeProps<T extends object> = {
  relatedObject: T;
  allowedFields?: string[];
  relatedObjectKey?: string;
};

/**
 * Finds the first primitive field in `relatedObject` that is allowed,
 * then displays its value inside a Badge. Throws if no allowed key is found.
 *
 * @param relatedObject - Single related resource relatedObject
 * @param allowedFields - List of field names permitted for display
 * @param relatedObjectKey - Key of the object, used to navigate to tab.
 * @returns A Badge containing the primitive value, or null for non-primitives
 * @throws InvalidRelatedObjectError When no allowed key exists
 */
export function RelatedObjectBadge<T extends object & { adminUrl?: string }>({
  relatedObject,
  allowedFields = DEFAULT_ALLOWED_FIELDS,
  relatedObjectKey,
}: RelatedObjectBadgeProps<T>) {
  const value = getObjectValue(relatedObject, allowedFields);

  const adminUrl = relatedObject.adminUrl;
  const label = `Bewerk ${value} in Open Zaak admin`; // TODO: add relatedObject type?

  return isPrimitive(value) ? (
    <Badge className="mykn-badge related-object-badge">
      <>
        {relatedObjectKey ? (
          <NavLink className="mykn-a" to={`#tab=${relatedObjectKey}`}>
            {value}
          </NavLink>
        ) : (
          value
        )}

        {adminUrl && (
          <A href={adminUrl} aria-label={label} target="_blank">
            <Outline.ArrowTopRightOnSquareIcon />
          </A>
        )}
      </>
    </Badge>
  ) : null;
}

/**
 * Retrieves a value from the given `object` whose key matches one of the
 * provided `allowedFields`.
 *
 * - The function searches through `allowedFields` in order and returns the value
 *   of the first field that exists in `relatedObject`.
 * - If none of the `allowedFields` are present, it falls back to the value
 *   of the first key in `relatedObject`.
 * - If `object` is empty, the function returns `null`.
 *
 * @typeParam T - The type of the object to extract a value from.
 * @param object - The object from which a value should be retrieved.
 * @param allowedFields - Optional array of field names prioritized for lookup.
 *                        Defaults to `DEFAULT_ALLOWED_FIELDS`.
 * @returns The value of the first matching field, the value of the first key
 *          in `object` if no match is found, or `null` if `relatedObject` is empty.
 */
export function getObjectValue<T extends object>(
  object: T,
  allowedFields: string[] = DEFAULT_ALLOWED_FIELDS,
): T[keyof T] | null {
  const key = getObjectKey(object, allowedFields);
  if (!key) return null;

  return object[key];
}

/**
 * Retrieves a key from the given `object` that matches one of the provided `allowedFields`.
 *
 * - The function searches through `allowedFields` in order and returns the first key
 *   that exists in `object`.
 * - If none of the `allowedFields` are present, it falls back to the first key
 *   of `object`.
 * - If `object` has no keys, the function returns `null`.
 *
 * @typeParam T - The type of the object to extract a key from.
 * @param object - The object from which a key should be retrieved.
 * @param allowedFields - Optional array of field names prioritized for lookup.
 *                        Defaults to `DEFAULT_ALLOWED_FIELDS`.
 * @returns The first matching key, the first key in `object` if no match is found,
 *          or `null` if `object` is empty.
 */
export function getObjectKey<T extends object>(
  object: T,
  allowedFields: string[] = DEFAULT_ALLOWED_FIELDS,
) {
  const keys = Object.keys(object);
  const allowedField = allowedFields.find((k) => keys.includes(k));
  const fallback = keys[0];
  return (allowedField || fallback) as keyof T;
}

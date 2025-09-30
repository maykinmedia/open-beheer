import { getUUIDFromString } from "~/lib/format/string.ts";

/**
 * Splits `obj.url` into parts, using the last part as UUID.
 * @param obj - An object which implements a `url` key (e.g. a Zaaktype).
 */
export const getZaaktypeUUID = (obj: { uuid: string } | { url: string }) => {
  return "uuid" in obj ? obj.uuid : getUUIDFromString(obj.url);
};

import { getUUIDFromString } from "~/lib/format/string.ts";

/**
 * Splits `obj.url` into parts, using the last part as UUID.
 * @param obj - An object which implements a `url` key (e.g. a Zaaktype).
 */
export const getZaaktypeUUID = (obj: { url: string }) =>
  getUUIDFromString(obj.url);

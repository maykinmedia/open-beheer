/**
 * Splits `obj.url` into parts, using the last part as UUID.
 * @param obj - An object which implements a `url` key (e.g. a Zaaktype).
 */
export const getZaaktypeUUID = (
  obj: { url: string }, // Possible todo: Replace with `getObjectUUID`?
) => obj.url.split("/").reverse()[0];

/**
 * Splits `obj.url` into parts, using the last part as UUID.
 * @param obj - An object which implements a `url` key (e.g. a Zaaktype).
 * @returns The UUID extracted from the URL.
 */
export const getObjectUUID = (obj: { url: string }): string =>
  obj.url.split("/").reverse()[0];

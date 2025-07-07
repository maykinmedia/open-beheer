/**
 * Splits `obj.url` into parts, using the last part as UUID.
 * @param obj - An object which implements a `url` key (e.g. a Zaaktype).
 */
export const getZaaktypeUUID = (obj: { url: string }) =>
  obj.url.split("/").reverse()[0];

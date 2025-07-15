/**
 * Takes an errors object and returns a `string[]` with correct messages.
 * Filters out irrelevant error codes like "key" or "code.
 * @param errors - The error response body.
 * @param join - Return a single string.
 * @param ignore - Ignore those fields
 * @returns A list of error messages or a joined string.
 */
export function collectErrors(
  errors: string,
  join?: false,
  ignore?: string[],
): string[];
export function collectErrors(
  errors: string,
  join: true,
  ignore?: string[],
): string;
export function collectErrors(
  errors: object,
  join?: false,
  ignore?: string[],
): string[];
export function collectErrors(
  errors: object,
  join: true,
  ignore?: string[],
): string;
export function collectErrors(
  errors: string | object,
  join?: boolean,
  ignore?: string[],
): string | string[];
export function collectErrors(
  errors: string | object,
  join = false,
  ignore = ["key", "code"],
): string | string[] {
  if (typeof errors === "string") {
    return join ? errors : [errors];
  }

  const flatten = Object.entries(errors || {})
    .filter(([key]) => !ignore.includes(key))
    .flatMap(([, value]) => value);

  const messages = flatten.reduce(
    (acc, val) => [...acc, ...collectErrors(val, false, ignore)],
    [],
  );

  return join ? messages.join("\n") : messages;
}

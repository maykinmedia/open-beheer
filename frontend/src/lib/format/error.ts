/**
 * Takes an errors object and returns a `string[]` with correct messages.
 * Filters out irrelevant error codes like "key" or "code.
 * @param errors - The error response body.
 * @param join - Whether to join the error messages and return a string.
 * @returns A list of error messages.
 */
export function collectErrors(errors: string | object): string[];
export function collectErrors(errors: string | object, join: false): string[];
export function collectErrors(errors: string | object, join: true): string;
export function collectErrors(
  errors: string | object,
  join = false,
): string | string[] {
  if (typeof errors === "string") {
    return join ? errors : [errors];
  }

  const flatten = Object.entries(errors || {})
    .filter(([key]) => !["key", "code"].includes(key))
    .map(([, value]) => value)
    .flat();

  const messages = flatten.reduce(
    (acc, val) => [...acc, ...collectErrors(val)],
    [] as string[],
  );

  return join ? messages.join("\n") : messages;
}

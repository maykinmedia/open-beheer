import { components } from "~/types";

/**
 * Takes an errors object and returns a `string[]` with correct messages.
 * Filters out irrelevant error codes like "key" or "code.
 * @param errors - The error response body.
 * @param join - Return a single string.
 * @param ignore - Ignore those fields
 * @returns A list of error messages or a joined string.
 */
export function collectErrorMessages(
  errors: string,
  join?: false,
  ignore?: string[],
): string[];
export function collectErrorMessages(
  errors: string,
  join: true,
  ignore?: string[],
): string;
export function collectErrorMessages(
  errors: object,
  join?: false,
  ignore?: string[],
): string[];
export function collectErrorMessages(
  errors: object,
  join: true,
  ignore?: string[],
): string;
export function collectErrorMessages(
  errors: string | object,
  join?: boolean,
  ignore?: string[],
): string | string[];
export function collectErrorMessages(
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
    (acc, val) => [...acc, ...collectErrorMessages(val, false, ignore)],
    [],
  );

  return join ? messages.join("\n") : messages;
}

/**
 * Returns invalidParams as errors object usable with admin-ui.
 * @param invalidParams - "invalidParams" section of error response.
 */
export function invalidParams2Errors(
  invalidParams: components["schemas"]["InvalidParam"][] = [],
): Record<string, string[]> {
  return invalidParams.reduce<Record<string, string[]>>(
    (acc, { name, reason }) => {
      const current = acc[name] || [];
      return { ...acc, [name]: [...current, reason] };
    },
    {},
  );
}

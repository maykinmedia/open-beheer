import { Primitive } from "@maykin-ui/admin-ui";

/**
 * Checks whether the given value is a primitive.
 *
 * A primitive is any value that is not an object (e.g. string, number, boolean, null, undefined, symbol, bigint).
 *
 * @param value - The value to check.
 * @returns True if the value is a primitive, false if it is an object.
 */
export function isPrimitive(value: Primitive | object): value is Primitive {
  return Object(value) !== value;
}

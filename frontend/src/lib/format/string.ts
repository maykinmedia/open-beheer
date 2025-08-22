/**
 * Extracts the first UUID found in a string.
 *
 * A UUID is expected in the canonical 8-4-4-4-12 format
 * (e.g., "550e8400-e29b-41d4-a716-446655440000").
 *
 * @param value - The input string which may contain a UUID.
 * @returns The first matched UUID as a string, or `null` if no UUID is found.
 */
export function getUUIDFromString(value: string): string | null {
  const uuidRegex =
    /\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b/i;
  const match = value.match(uuidRegex);
  return match ? match[0] : null;
}

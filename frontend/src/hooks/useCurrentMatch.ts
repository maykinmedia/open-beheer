import { UIMatch, useMatches } from "react-router";

/**
 * Returns the deepest matched route from the current route hierarchy.
 *
 * Useful for accessing metadata such as `id`, `params`, `handle`, or route-specific data
 * defined on the most specific (child) route in the current match.
 *
 * @returns The last matched route object, or `undefined` if no matches exist.
 */
export function useCurrentMatch() {
  const matches = useMatches();
  return [...matches].pop() as UIMatch;
}

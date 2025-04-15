import { UIMatch, useMatches } from "react-router";
import { routes } from "~/routes.tsx";

/**
 * Returns the child routes for a given route ID.
 *
 * @param id - The ID of the parent route to look up, must be present in `ROUTE_IDS`.
 * @returns An array of child route objects, or an empty array if none are found.
 */
export function useChildRoutes(id?: string) {
  const matches = useMatches();

  for (const currentMatch of matches.reverse()) {
    const childRoutes = _resolveChildRoutes(id, currentMatch);
    if (childRoutes.length) {
      return childRoutes;
    }
  }
  return [];
}

/**
 * Returns the child routes for a given route ID.
 *
 * @param id - The ID of the parent route to look up, must be present in `ROUTE_IDS`.
 * @param currentMatch - The current React Router match.
 * @param haystack - Used internally when this hooks recurses to find a nested route.
 * @returns An array of child route objects, or an empty array if none are found.
 */
function _resolveChildRoutes(
  id: string | undefined,
  currentMatch: UIMatch | undefined,
  haystack = routes,
) {
  const _id = typeof id === "undefined" ? currentMatch?.id || "" : id;

  // if (Object.values(ROUTE_IDS).includes(_id)) {
  const currentRoute = haystack.find((route) => route.id === _id);
  if (currentRoute) {
    return currentRoute.children || [];
  }

  // Recurse through child routes.
  const _haystack = haystack
    .filter((route) => route.children?.length)
    .flatMap((route) => route.children || []);

  if (_haystack.length) {
    return _resolveChildRoutes(_id, currentMatch, _haystack);
  }
  // }
  return [];
}

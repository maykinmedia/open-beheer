import { RouteObject } from "react-router";
import { routes } from "~/routes.tsx";

/**
 * Returns the route object with the given ID from the application's route tree.
 *
 * @param id - The ID of the route to find.
 * @returns The matching RouteObject, or undefined if not found.
 */
export function useRoute(id: string): RouteObject | undefined {
  return _useRoute(id, routes)?.[0];
}

/**
 * Returns the path of route objects leading to the route with the given ID.
 *
 * @param id - The ID of the route to find.
 * @returns An array of RouteObjects representing the path, or undefined if not found.
 */
export function useRoutesPath(id: string): RouteObject[] | undefined {
  return _useRoute(id, routes)?.[1];
}

/**
 * Recursively searches for a route by ID within a nested route structure.
 *
 * @param id - The ID of the route to find.
 * @param haystack - The list of RouteObjects to search through.
 * @param path - The accumulated path of routes traversed so far.
 * @returns A tuple containing the matching RouteObject and the path to it, or undefined if not found.
 */
function _useRoute(
  id: string,
  haystack: RouteObject[],
  path: RouteObject[] = [],
): [RouteObject, RouteObject[]] | undefined {
  for (const needle of haystack) {
    const updatedPath = [...path, needle];

    if (id === needle.id) {
      return [needle, updatedPath];
    }

    if (needle.children) {
      const nneedle = _useRoute(id, needle.children, updatedPath);

      if (nneedle) {
        return nneedle;
      }
    }
  }

  return undefined;
}

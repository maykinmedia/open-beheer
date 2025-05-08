import { ucFirst } from "@maykin-ui/admin-ui";
import { useMatches } from "react-router";

/**
 * Generates breadcrumb items based on the current route matches.
 *
 * Each breadcrumb item includes a capitalized label derived from the route `id`
 * and a corresponding `href` from the route `pathname`. Routes with a pathname
 * of `/` are excluded.
 *
 * @returns An array of breadcrumb items with `label` and `href` properties.
 */
export function useBreadcrumbItems() {
  const matches = useMatches();
  return matches
    .filter((m) => m.pathname !== "/")
    .map((m) => ({
      label: ucFirst(m.id),
      href: m.pathname,
    }));
}

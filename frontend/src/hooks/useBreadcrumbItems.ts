import { string2Title } from "@maykin-ui/client-common";
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
  const result = matches
    .filter((m) => m.pathname !== "/") // Exclude root
    .filter(
      // Exclude list views
      (m) =>
        !(
          m.loaderData &&
          typeof m.loaderData == "object" &&
          "results" in m.loaderData
        ),
    )
    .map((m) => ({
      label:
        //@ts-expect-error - loaderdata is untyped here.
        m.loaderData?.result?.identificatie ||
        //@ts-expect-error - loaderdata is untyped here.
        m.loaderData?.result?.omschrijving ||
        string2Title(m.id),
      href: m.pathname,
    }));
  return result;
}

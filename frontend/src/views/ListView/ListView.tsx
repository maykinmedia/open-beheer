import { FieldSet, ListTemplate } from "@maykin-ui/admin-ui";
import { useCallback } from "react";
import {
  useLocation,
  useNavigation,
  useOutlet,
  useSearchParams,
} from "react-router";
import { ListResponse } from "~/api/types";
import { useBreadcrumbItems } from "~/hooks";

export type ListViewProps<T extends object> = ListResponse<T> & {
  fieldsets: FieldSet<T>[];
};

/**
 * Displays a paginated list of items using a data grid.
 *
 * The primary action (click) shows item details in a side pane.
 * Ctrl+click or Cmd+click navigates to the item's detail route in fullscreen.
 *
 * @typeParam T - The type of items in the list. Must include at least `uuid` and `identificatie` fields.
 *
 * @param fields - The field's configuration.
 * @param pagination - The paginator configuration.
 * @param results - The list of items to render in the data grid.
 * @param fieldsets - Optional custom fieldsets used for rendering item details.
 * @param fieldsets - Optional custom fieldsets used for rendering item details.
 */
export function ListView<T extends object>({
  fields,
  pagination,
  results,
}: ListViewProps<T>) {
  const { pathname } = useLocation();
  const { state } = useNavigation();
  const outlet = useOutlet();
  const [urlSearchParams, setURLSearchParams] = useSearchParams();
  const breadcrumbItems = useBreadcrumbItems();

  /**
   * Gets called when the page number changes.
   * @param page - The new page number.
   */
  const handlePageChange = useCallback(
    (page: number) => {
      updateSanitizedURLSearchParams({ page });
    },
    [urlSearchParams],
  );

  /**
   * Sanitizes, then updates `urlSearchParams`, this causes the loader to refresh the
   * page.
   * @param params - The updates to apply to `urlSearchParams`.
   */
  const updateSanitizedURLSearchParams = useCallback(
    (params: Record<string, unknown>) => {
      const newParams = { ...urlSearchParams, ...params };

      const filteredEntries = Object.fromEntries(
        Object.entries(newParams)
          .filter(([, v]) => v !== null)
          .map(([k, v]) => [k, v.toString()]),
      );

      setURLSearchParams(filteredEntries);
    },
    [urlSearchParams],
  );

  return (
    outlet || (
      <ListTemplate
        breadcrumbItems={breadcrumbItems}
        dataGridProps={{
          objectList: results.map((row) => ({
            ...row,
            // @ts-expect-error - Assume uuid.
            href: row.uuid ? `${pathname}/${row.uuid}` : undefined,
          })),
          decorate: true,
          fields: fields,
          height: "fill-available-space",
          showPaginator: Boolean(pagination),
          loading: state !== "idle",
          paginatorProps: pagination,
          onPageChange: handlePageChange,
        }}
      />
    )
  );
}

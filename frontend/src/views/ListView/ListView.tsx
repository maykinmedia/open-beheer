import { ListTemplate } from "@maykin-ui/admin-ui";
import React, { useCallback } from "react";
import {
  useNavigate,
  useNavigation,
  useOutlet,
  useSearchParams,
} from "react-router";
import { ListResponse } from "~/api/types";
import { useBreadcrumbItems } from "~/hooks";

export type ListViewProps<T extends object> = ListResponse<T> & {
  getHref?: (obj: T) => string;
};

/**
 * Displays a paginated list of items using a data grid.
 *
 * The primary action (click) shows item details in a side pane.
 * Ctrl+click or Cmd+click navigates to the item's detail route in fullscreen.
 *
 * @typeParam T - The type of items in the list. Must include at least `uuid` and
 *  `identificatie` fields.
 *
 * @param fields - The field's configuration.
 * @param pagination - The paginator configuration.
 * @param results - The list of items to render in the data grid.
 * @param getHref - A function that if set, receives the row and should return a
 *  URL to navigate to.
 */
export function ListView<T extends object>({
  fields,
  pagination,
  results,
  getHref,
}: ListViewProps<T>) {
  const navigate = useNavigate();
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

  /**
   * Gets called when a row's identifier is clicked.
   * @param event - The mouse event.
   * @param data - The row data.
   */
  const handleClick = useCallback(
    (event: React.MouseEvent<HTMLAnchorElement>, data: T) => {
      event.preventDefault();
      if (getHref) {
        navigate(getHref(data));
      }
    },
    [getHref],
  );

  return (
    outlet || (
      <ListTemplate
        breadcrumbItems={breadcrumbItems}
        dataGridProps={{
          objectList: results.map((row) => ({
            ...row,
            href: getHref && getHref(row),
          })),
          decorate: true,
          fields: fields,
          height: "fill-available-space",
          showPaginator: Boolean(pagination),
          loading: state !== "idle",
          paginatorProps: pagination,
          onClick: handleClick,
          onPageChange: handlePageChange,
        }}
      />
    )
  );
}

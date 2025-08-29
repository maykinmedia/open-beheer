import { DataGridProps, ListTemplate } from "@maykin-ui/admin-ui";
import { useCallback } from "react";
import { useNavigate, useNavigation, useOutlet } from "react-router";
import { ListResponse } from "~/api/types";
import { useBreadcrumbItems, useCombinedSearchParams } from "~/hooks";

export type ListViewProps<T extends object> = ListResponse<T> & {
  getHref?: (obj: T) => string;
  datagridProps?: DataGridProps<T>;
  toolbarItems?: DataGridProps<T>["toolbarItems"];
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
 * @param datagridProps - DataGrid props.
 * @param fields - The field's configuration.
 * @param pagination - The paginator configuration.
 * @param results - The list of items to render in the data grid.
 * @param getHref - A function that if set, receives the row and should return a
 *  URL to navigate to.
 * @param toolbarItems - Optional extra toolbar items to add to the data grid.
 */
export function ListView<T extends object>({
  datagridProps,
  fields,
  pagination,
  results,
  getHref,
  toolbarItems,
}: ListViewProps<T>) {
  const navigate = useNavigate();
  const { state } = useNavigation();
  const outlet = useOutlet();
  const breadcrumbItems = useBreadcrumbItems();
  const [urlSearchParams, setCombinedSearchParams] = useCombinedSearchParams(0);

  /**
   * Gets called when the page number changes.
   * @param page - The new page number.
   */
  const handlePageChange = (page: number) => {
    setCombinedSearchParams({ page: page.toString() });
  };

  /**
   * Gets called when a row's identifier is clicked.
   * @param event - The mouse event.
   * @param data - The row data.
   */
  const handleClick = useCallback(
    (event: React.MouseEvent, data: T) => {
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
          fields: fields,
          boolProps: { explicit: true },
          decorate: true,
          height: "fill-available-space",
          showPaginator: Boolean(pagination),
          toolbarItems: toolbarItems,
          loading: state !== "idle",
          page: parseInt(urlSearchParams.get("page") || "1"),
          paginatorProps: pagination,
          onClick: handleClick,
          onPageChange: handlePageChange,
          ...datagridProps,
        }}
      />
    )
  );
}

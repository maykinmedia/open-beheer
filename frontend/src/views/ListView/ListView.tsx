import {
  AttributeGrid,
  Body,
  DataGridProps,
  FieldSet,
  ListTemplate,
  Modal,
  Outline,
  SerializedFormData,
  ToolbarItem,
  TypedField,
} from "@maykin-ui/admin-ui";
import React, {
  SyntheticEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  useLocation,
  useNavigate,
  useNavigation,
  useOutlet,
} from "react-router";
import { ListResponse } from "~/api/types";
import { useBreadcrumbItems, useCombinedSearchParams } from "~/hooks";

export type ListViewProps<T extends object> = ListResponse<T> & {
  fieldsets: FieldSet<T>[];
  toolbarItems?: DataGridProps["toolbarItems"];
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
 * @param fieldsets - Optional custom fieldsets used for rendering item details.
 * @param pagination - The paginator configuration.
 * @param results - The list of items to render in the data grid.
 * @param toolbarItems - Optional extra toolbar items to add to the data grid.
 */
export function ListView<T extends object>({
  fields,
  fieldsets,
  pagination,
  results,
  toolbarItems,
}: ListViewProps<T>) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { state } = useNavigation();
  const outlet = useOutlet();
  const [activeItem, setActiveItem] = useState<T>();
  const breadcrumbItems = useBreadcrumbItems();
  const [urlSearchParams, setCombinedSearchParams] = useCombinedSearchParams(0);

  // Clean up some OAS/Admin-ui mismatches.
  const sanitizedFields: TypedField<T>[] = useMemo(
    () =>
      fields
        .filter((f) =>
          ["boolean", "number", "integer", "string", "date"].includes(f.type),
        )
        .map((f) => ({ ...f, type: f.type === "integer" ? "number" : f.type })),
    [fields],
  );

  // Ctrl + click (or command + click on Mac) triggers secondary action.
  const ACTIONS = {
    // The primary action (click) shows item details in a side pane.
    PRIMARY: (data: T) => {
      if (
        // @ts-expect-error - Assume uuid.
        data.uuid &&
        // @ts-expect-error - Assume uuid.
        data.uuid === activeItem?.uuid
      ) {
        // @ts-expect-error - Assume uuid.
        navigate(data.uuid);
      }
      setActiveItem(data);
    },

    // Ctrl+click or Cmd+click navigates to the item's detail route in fullscreen.
    SECONDARY: (data: T) => {
      // @ts-expect-error - Assume uuid.
      return data.uuid ? navigate(data.uuid) : undefined;
    },
  };

  /**
   * Gets called when a row's identifier is clicked.
   * @param event - The mouse event.
   * @param data - The row data.
   */
  const handleClick = useCallback(
    (event: React.MouseEvent<HTMLAnchorElement>, data: T) => {
      event.preventDefault();
      if (event.metaKey || event.ctrlKey || event.button === 1) {
        return ACTIONS.SECONDARY(data);
      }
      return ACTIONS.PRIMARY(data);
    },
    [activeItem, setActiveItem],
  );

  /**
   * Gets called when a filter is applied.
   * @param event - The mouse event.
   * @param data - The row data.
   */
  const handleFilter = useCallback(
    (data: SerializedFormData) => {
      setCombinedSearchParams(data as Record<string, string>);
    },
    [urlSearchParams],
  );

  /**
   * Gets called when the page number changes.
   * @param page - The new page number.
   */
  const handlePageChange = useCallback(
    (page: number) => {
      setCombinedSearchParams({ page: page.toString() });
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
          fields: sanitizedFields,
          height: "fill-available-space",
          showPaginator: Boolean(pagination),
          toolbarItems: toolbarItems,
          loading: state !== "idle",
          paginatorProps: pagination,
          onClick: handleClick,
          onPageChange: handlePageChange,
          onFilter: handleFilter,
        }}
      >
        {activeItem && (
          <ListItemDetails<T>
            object={activeItem}
            fieldsets={fieldsets}
            actions={[
              {
                justify: true,
                variant: "transparent",
                children: (
                  <>
                    <Outline.PencilIcon /> Bewerken
                  </>
                ),
                onClick: () =>
                  // @ts-expect-error - Assume uuid.
                  activeItem.uuid
                    ? // @ts-expect-error - Assume uuid.
                      navigate(`${activeItem?.uuid}`)
                    : undefined,
              },
            ]}
            onClose={() => setActiveItem(undefined)}
          />
        )}
      </ListTemplate>
    )
  );
}

/**
 * Displays details of a selected object using fieldsets.
 *
 * If no object is selected, a placeholder title is shown instead.
 *
 * @typeParam T - The type of the object. Must include a `identificatie` field.
 *
 * @param object - The selected object to display details for.
 * @param fieldsets - Optional custom fieldsets configuration.
 * @param actions - Optional toolbar items shown as actions.
 * @param defaultTitle - Title shown when no object is selected.
 * @param onClose - Gets called when the modal is closed.
 */
function ListItemDetails<T extends object>({
  object,
  fieldsets,
  actions,
  defaultTitle = "Geen item geselecteerd",
  onClose,
}: {
  object?: T;
  fieldsets?: FieldSet<T>[];
  actions?: ToolbarItem[];
  defaultTitle?: string;
  onClose?: React.EventHandler<SyntheticEvent<HTMLDialogElement>>;
}) {
  const [open, setOpen] = useState<boolean>();

  useEffect(() => {
    setOpen(Boolean(object));
  }, [object]);

  const defaultFieldsets: FieldSet<T>[] = object
    ? [["", { fields: Object.keys(object) as (keyof T)[], span: 12 }]]
    : [];

  return (
    <Modal
      actions={actions}
      open={open}
      position="side"
      showLabelClose={true}
      size="m"
      // @ts-expect-error - Assume identificatie
      title={object?.identificatie ? object.identificatie : defaultTitle}
      type="dialog"
      restoreAutofocus={true}
      onClose={(e) => {
        onClose?.(e);
        setOpen(false);
      }}
    >
      <Body>
        <AttributeGrid<T>
          object={object || ({} as T)}
          fieldsets={object ? fieldsets || defaultFieldsets : []}
        />
      </Body>
    </Modal>
  );
}

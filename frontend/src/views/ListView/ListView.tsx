import {
  AttributeGrid,
  Body,
  Card,
  FieldSet,
  ListTemplate,
  Outline,
  ToolbarItem,
} from "@maykin-ui/admin-ui";
import React, { useCallback, useState } from "react";
import { useLocation, useNavigate, useOutlet } from "react-router";

/**
 * Displays a paginated list of items using a data grid.
 *
 * The primary action (click) shows item details in a side pane.
 * Ctrl+click or Cmd+click navigates to the item's detail route in fullscreen.
 *
 * @typeParam T - The type of items in the list. Must include at least `id` and `name` fields.
 *
 * @param objectList - The list of items to render in the data grid.
 * @param fieldsets - Optional custom fieldsets used for rendering item details.
 * @param title - Optional title shown above the list.
 */
export function ListView<T extends { id: number | string; name: string }>({
  objectList,
  fieldsets,
  title = "Resultaten",
}: {
  objectList: T[];
  fieldsets?: FieldSet<T>[];
  title?: string;
}) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const outlet = useOutlet();
  const [activeItem, setActiveItem] = useState<T>();

  // Ctrl + click (or command + click on Mac) triggers secondary action.
  const ACTIONS = {
    // The primary action (click) shows item details in a side pane.
    PRIMARY: (data: T) => setActiveItem(data),

    // Ctrl+click or Cmd+click navigates to the item's detail route in fullscreen.
    SECONDARY: (data: T) => navigate(data.id.toString()),
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
    [setActiveItem],
  );

  return (
    outlet || (
      <ListTemplate
        cardProps={{ direction: "row-reverse" }}
        dataGridProps={{
          objectList: objectList.map((row) => ({
            ...row,
            href: `${pathname}/${row.id}`,
          })),
          height: "fill-available-space",
          showPaginator: true,
          title,
          onClick: handleClick,
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
                onClick: () => navigate(`${activeItem?.id}`),
              },
              {
                justify: true,
                variant: "transparent",
                children: (
                  <>
                    <Outline.XMarkIcon /> Sluiten
                  </>
                ),
                onClick: () => setActiveItem(undefined),
              },
            ]}
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
 * @typeParam T - The type of the object. Must include a `name` field.
 *
 * @param object - The selected object to display details for.
 * @param fieldsets - Optional custom fieldsets configuration.
 * @param actions - Optional toolbar items shown as actions.
 * @param defaultTitle - Title shown when no object is selected.
 */
function ListItemDetails<T extends { name: string }>({
  object,
  fieldsets,
  actions,
  defaultTitle = "Geen item geselecteerd",
}: {
  object?: T;
  fieldsets?: FieldSet<T>[];
  actions?: ToolbarItem[];
  defaultTitle?: string;
}) {
  const defaultFieldsets: FieldSet<T>[] = object
    ? [["", { fields: Object.keys(object) as (keyof T)[], span: 12 }]]
    : [];

  return (
    <Card
      actions={object ? actions : undefined}
      title={object ? object.name : defaultTitle}
    >
      <Body>
        <AttributeGrid<T>
          object={object || ({} as T)}
          fieldsets={object ? fieldsets || defaultFieldsets : []}
        />
      </Body>
    </Card>
  );
}

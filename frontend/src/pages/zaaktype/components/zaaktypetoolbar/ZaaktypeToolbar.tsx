import { Outline, Solid, Toolbar, ToolbarItem } from "@maykin-ui/admin-ui";
import React, { useMemo } from "react";
import { useLoaderData } from "react-router";
import { ZaaktypeLoaderData } from "~/pages";

type ZaaktypeToolbarProps = {
  onCancel: React.MouseEventHandler;
  onEdit: React.MouseEventHandler;
  onPublish: React.MouseEventHandler;
  onSave: React.MouseEventHandler;
  onSaveAs: React.MouseEventHandler;
  onVersionCreate: React.MouseEventHandler;
};

/**
 * Renders the bottom toolbar containing (primary) actions.
 */
export function ZaaktypeToolbar({
  onCancel,
  onEdit,
  onPublish,
  onSave,
  onSaveAs,
  onVersionCreate,
}: ZaaktypeToolbarProps) {
  const { result, versions } = useLoaderData() as ZaaktypeLoaderData;
  const isEditing =
    new URLSearchParams(location.search).get("editing") === "true";

  const button = useMemo<ToolbarItem[]>(() => {
    if (versions?.some((v) => v.concept)) {
      if (!isEditing) {
        return [
          {
            componentType: "button",
            children: (
              <>
                <Solid.PencilSquareIcon />
                Bewerken
              </>
            ),
            variant: "primary",
            onClick: onEdit,
          },
        ];
      } else {
        return [
          {
            componentType: "button",
            children: (
              <>
                <Outline.DocumentDuplicateIcon />
                Opslaan als
              </>
            ),
            variant: "transparent",
            onClick: onSaveAs,
          },
          "spacer",
          {
            componentType: "button",
            children: (
              <>
                <Outline.NoSymbolIcon />
                Annuleren
              </>
            ),
            variant: "transparent",
            onClick: onCancel,
          },
          {
            componentType: "button",
            children: (
              <>
                <Outline.CloudArrowUpIcon />
                Publiceren
              </>
            ),
            variant: "transparent",
            onClick: onPublish,
          },
          {
            componentType: "button",
            children: (
              <>
                <Outline.ArrowDownTrayIcon />
                Opslaan
              </>
            ),
            variant: "primary",
            onClick: onSave,
          },
        ];
      }
    } else {
      return [
        {
          componentType: "button",
          children: (
            <>
              <Outline.PlusIcon />
              Nieuwe Versie
            </>
          ),
          variant: "primary",
          onClick: onVersionCreate,
        },
      ];
    }
  }, [result, isEditing, onEdit, onSave, onVersionCreate]);

  return (
    <Toolbar
      align="end"
      pad
      variant="transparent"
      sticky={"bottom"}
      items={button}
    ></Toolbar>
  );
}

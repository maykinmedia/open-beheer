import { Outline, Solid, Toolbar } from "@maykin-ui/admin-ui";
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

  const button = useMemo(() => {
    if (versions?.some((v) => v.concept)) {
      if (!isEditing) {
        return [
          {
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

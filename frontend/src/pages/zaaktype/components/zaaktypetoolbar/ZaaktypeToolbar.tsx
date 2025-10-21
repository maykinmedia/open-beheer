import { Outline, Solid, Toolbar } from "@maykin-ui/admin-ui";
import React, { useMemo } from "react";
import { useLoaderData } from "react-router";
import { useCombinedSearchParams } from "~/hooks";
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
  const [combinedSearchParams] = useCombinedSearchParams();

  const button = useMemo(() => {
    if (versions?.some((v) => v.concept)) {
      if (!combinedSearchParams.get("editing")) {
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
                <Outline.NoSymbolIcon />
                Annuleren
              </>
            ),
            variant: "transparent",
            onClick: onCancel,
          },
          "spacer",
          {
            children: (
              <>
                <Outline.DocumentDuplicateIcon />
                Opslaan als nieuw Zaaktype
              </>
            ),
            variant: "transparent",
            onClick: onSaveAs,
          },
          {
            children: (
              <>
                <Outline.ArrowDownTrayIcon />
                Opslaan en afsluiten
              </>
            ),
            variant: "transparent",
            onClick: onSave,
          },
          {
            children: (
              <>
                <Outline.CloudArrowUpIcon />
                Publiceren
              </>
            ),
            variant: "primary",
            onClick: onPublish,
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
  }, [result, combinedSearchParams, onEdit, onSave, onVersionCreate]);

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

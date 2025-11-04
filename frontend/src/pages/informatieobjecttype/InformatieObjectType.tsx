import {
  AttributeGrid,
  Body,
  CardBaseTemplate,
  FieldSet,
  H2,
  Outline,
  Solid,
  Toolbar,
  ToolbarItem,
} from "@maykin-ui/admin-ui";
import { ucFirst } from "@maykin-ui/client-common";
import { useCallback, useMemo, useState } from "react";
import { useLoaderData } from "react-router";
import { useBreadcrumbItems, useCombinedSearchParams } from "~/hooks";
import { useSubmitAction } from "~/hooks/useSubmitAction";
import { convertFieldsetsToTabConfig } from "~/lib";

import { TabConfig } from "../zaaktype";
import {
  BackendIOT,
  InformatieObjectTypeAction,
  PatchedBackendIOT,
} from "./informatieobjecttype.action";
import { InformatieObjectTypeLoaderData } from "./informatieobjecttype.loader";

export function InformatieObjectTypePage() {
  const { fields, fieldsets, result } =
    useLoaderData() as InformatieObjectTypeLoaderData;
  const breadcrumbItems = useBreadcrumbItems();
  const submitAction = useSubmitAction<InformatieObjectTypeAction>();
  const [combinedSearchParams] = useCombinedSearchParams();
  const isEditing = Boolean(combinedSearchParams.get("editing"));
  const [newIOTData, setNewIOTData] = useState<PatchedBackendIOT>(result);

  const fieldSetConfigs = useMemo<TabConfig<PatchedBackendIOT>[]>(
    convertFieldsetsToTabConfig<PatchedBackendIOT>(fieldsets),
    [JSON.stringify([fields, fieldsets])],
  );

  const onToggleEditOn = useCallback<React.MouseEventHandler>(() => {
    submitAction({
      type: "SET_EDIT_MODE_ON",
      payload: {},
    });
  }, []);

  const onCancel = useCallback<React.MouseEventHandler>(() => {
    submitAction({
      type: "SET_EDIT_MODE_OFF",
      payload: {},
    });
  }, []);

  const onSave = useCallback<React.MouseEventHandler>(() => {
    submitAction({
      type: "UPDATE",
      payload: newIOTData,
    });
  }, [newIOTData]);

  const onSaveAndPublish = useCallback<React.MouseEventHandler>(() => {
    submitAction({
      type: "UPDATE_AND_PUBLISH",
      payload: newIOTData,
    });
  }, [newIOTData]);

  const onPublish = useCallback<React.MouseEventHandler>(() => {
    submitAction({
      type: "PUBLISH",
      payload: {},
    });
  }, []);

  const getButtons = useCallback(
    (result: BackendIOT, isEditing: boolean): ToolbarItem[] => {
      if (result.concept && !isEditing)
        return [
          {
            children: (
              <>
                <Solid.PencilSquareIcon />
                Bewerken
              </>
            ),
            variant: "secondary",
            onClick: onToggleEditOn,
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

      if (isEditing)
        return [
          {
            children: (
              <>
                <Outline.NoSymbolIcon />
                Annuleren
              </>
            ),
            variant: "danger",
            onClick: onCancel,
          },
          "spacer",
          {
            children: (
              <>
                <Outline.CloudArrowUpIcon />
                Opslaan en publiceren
              </>
            ),
            variant: "secondary",
            onClick: onSaveAndPublish,
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

      return [];
    },
    [newIOTData],
  );

  // We know that the IOT does not have expansions,
  // so we can narrow the type further
  if (fieldSetConfigs[0].view !== "AttributeGrid") {
    // This should not happen.
    throw new Error("Something went wrong while rendering the data.");
  }

  const fieldsetsWithFieldInfo = fieldSetConfigs[0].sections[0].fieldsets.map(
    (fieldset) =>
      [
        fieldset[0],
        {
          ...fieldset[1],
          fields: fieldset[1].fields.map((fieldsetField) =>
            fields.find((field) => field.name === fieldsetField),
          ),
        },
      ] as FieldSet<PatchedBackendIOT>,
  );

  return (
    <CardBaseTemplate
      breadcrumbItems={breadcrumbItems}
      cardProps={{
        justify: "space-between",
      }}
    >
      <Body fullHeight>
        <H2>{ucFirst(result.omschrijving)}</H2>

        <AttributeGrid
          object={isEditing ? { ...result, ...newIOTData } : result}
          editable={isEditing ? undefined : false}
          editing={isEditing}
          fieldsets={fieldsetsWithFieldInfo}
          onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
            setNewIOTData({
              ...newIOTData,
              [event.target.name]: event.target.value,
            })
          }
        />
      </Body>

      <Toolbar
        align="end"
        pad
        variant="transparent"
        sticky={"bottom"}
        items={getButtons(result, isEditing)}
      ></Toolbar>
    </CardBaseTemplate>
  );
}

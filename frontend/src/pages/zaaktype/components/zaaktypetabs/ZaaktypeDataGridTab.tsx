import {
  Field,
  Option,
  TypedField,
  getFieldName,
  useDialog,
} from "@maykin-ui/admin-ui";
import { invariant, string2Title } from "@maykin-ui/client-common";
import { JSX, useCallback, useEffect, useMemo, useState } from "react";
import { useLoaderData, useLocation, useParams } from "react-router";
import { ArchiveForm } from "~/components";
import {
  RelatedObjectDataGrid,
  RelatedObjectDataGridAction,
} from "~/components/related";
import { DataGridTabConfig, TargetType, ZaaktypeLoaderData } from "~/pages";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { RelatedObject, components } from "~/types";

export type ZaaktypeDataGridProps = {
  object: TargetType;
  tabConfig: DataGridTabConfig<TargetType>;
  onTabActionsChange: (
    tabConfig: DataGridTabConfig<TargetType>,
    actions: ZaaktypeAction[],
  ) => void;
};

type ResultaatType = components["schemas"]["ResultaatTypeWithUUID"];

/**
 * Renders a DataGrid tab for a Zaaktype.
 * Displays related objects and converts user actions into ZaaktypeActions.
 */
export function ZaaktypeDataGridTab({
  object,
  tabConfig,
  onTabActionsChange,
}: ZaaktypeDataGridProps) {
  const { fields } = useLoaderData() as ZaaktypeLoaderData;
  const location = useLocation();
  const { serviceSlug } = useParams();
  invariant(serviceSlug, "serviceSlug must be provided!");

  const isEditing =
    new URLSearchParams(location.search).get("editing") === "true";

  const hookDialog = useDialog();
  const [hookDialogState, setHookDialogState] = useState<{
    open: boolean;
    title?: string;
    body?: JSX.Element;
  }>();

  // Opens a dialog whenever hookDialogState updates
  useEffect(() => {
    if (!hookDialogState) return;
    hookDialog(hookDialogState.title || "", hookDialogState.body, undefined, {
      open: hookDialogState.open,
    });
  }, [hookDialogState]);

  /**
   * Converts DataGrid actions (create, update, delete) into ZaaktypeActions
   * with the appropriate metadata for backend submission.
   */
  const handleActionsChange = useCallback(
    (actions: RelatedObjectDataGridAction<RelatedObject<TargetType>>[]) => {
      const _tabConfig = tabConfig as DataGridTabConfig<TargetType>;
      invariant(object.uuid, "Zaaktype must have uuid set!");

      const zaaktypeActions: ZaaktypeAction[] = actions.map((action) => {
        const payloadBase = {
          serviceSlug,
          zaaktypeUuid: object.uuid!,
          relatedObjectKey: _tabConfig.key,
        };

        switch (action.type) {
          case "CREATE":
            return {
              type: "ADD_RELATED_OBJECT",
              payload: { ...payloadBase, relatedObject: action.payload },
            };
          case "UPDATE":
            return {
              type: "EDIT_RELATED_OBJECT",
              payload: { ...payloadBase, relatedObject: action.payload },
            };
          case "DELETE":
            invariant(action.payload.uuid, "action.payload.uuid must be set!");
            return {
              type: "DELETE_RELATED_OBJECT",
              payload: {
                ...payloadBase,
                relatedObjectUuid: action.payload.uuid!,
              },
            };
          default:
            // @ts-expect-error - never as this should "never" happen.
            throw new Error("Unknown action type: " + action.type);
        }
      });

      onTabActionsChange(tabConfig, zaaktypeActions);
    },
    [tabConfig, object, onTabActionsChange],
  );

  /**
   * Pre-commit hook for related objects.
   * Allows validating or modifying related objects before saving.
   * Returning `false` cancels the change.
   */
  const relatedObjectHook = async (
    relatedObject: RelatedObject<TargetType>,
    actionType: RelatedObjectDataGridAction<typeof relatedObject>["type"],
  ): Promise<false | RelatedObject<TargetType>> => {
    switch (tabConfig.key) {
      case "resultaattypen":
        return await resultaatTypeHook(
          relatedObject as components["schemas"]["ResultaatTypeWithUUID"],
          actionType,
        );
    }
    return relatedObject;
  };

  /**
   * Pre-commit hook for ResultaatType objects.
   * Opens a dialog for additional data entry (ArchiveForm) before committing.
   */
  const resultaatTypeHook = useCallback(
    async (
      resultaatType: ResultaatType,
      actionType: RelatedObjectDataGridAction<ResultaatType>["type"],
    ): Promise<ResultaatType | false> => {
      if (actionType.toUpperCase().includes("DELETE")) return resultaatType;

      return new Promise((resolve, reject) => {
        const selectielijstklasseOptions = fields.find(
          (field) =>
            field.name === "_expand.resultaattypen.selectielijstklasse",
        )?.options as Option[] | undefined;

        invariant(
          selectielijstklasseOptions,
          "Failed to locate selectielijstklasse field!",
        );

        setHookDialogState({
          open: true,
          title: string2Title(tabConfig.label),
          body: (
            <ArchiveForm
              resultaatType={resultaatType}
              selectielijstklasseOptions={selectielijstklasseOptions}
              onSubmit={({
                selectielijstklasse,
                brondatumArchiefProcedure,
              }) => {
                setHookDialogState({ open: false });

                const resultaatTypeOmschrijvingField = fields.find(
                  (f) =>
                    f.name ===
                    "_expand.resultaattypen.resultaattypeomschrijving",
                );

                const defaultResultaatTypeOmschrijving =
                  actionType === "CREATE"
                    ? (resultaatTypeOmschrijvingField?.options?.find(
                        ({ label }) =>
                          label.toLowerCase() ===
                          brondatumArchiefProcedure.afleidingswijze.toLowerCase(),
                      )?.value as string | undefined)
                    : undefined;

                resolve({
                  ...resultaatType,
                  selectielijstklasse,
                  resultaattypeomschrijving:
                    defaultResultaatTypeOmschrijving ||
                    resultaatType.resultaattypeomschrijving,
                  brondatum_archiefprocedure: brondatumArchiefProcedure,
                } as ResultaatType);
              }}
              onCancel={() => {
                setHookDialogState({ open: false });
                reject(false);
              }}
            />
          ),
        });
      });
    },
    [fields, hookDialogState],
  );

  /**
   * Renders a RelatedObjectDataGrid containing related items.
   * Provides editing capabilities and integrates with action hooks.
   */
  const contents = useMemo(() => {
    const key = tabConfig.key;
    const relatedObjects = object._expand[key] || [];
    invariant(
      Array.isArray(relatedObjects),
      "relatedObjects must be an Array for RelatedObjectDataGrid!",
    );

    const fieldSetFields = tabConfig.fieldset[1].fields.map((fieldName) => {
      const field = fields.find(
        (field) => getFieldName(field as Field) === getFieldName(fieldName),
      );
      invariant(field, "field not found!");
      return field as TypedField;
    });

    return (
      <RelatedObjectDataGrid
        fields={fieldSetFields}
        isEditing={isEditing}
        objectList={relatedObjects}
        onActionsChange={handleActionsChange}
        hook={relatedObjectHook}
      />
    );
  }, [
    tabConfig,
    object,
    fields,
    isEditing,
    handleActionsChange,
    relatedObjectHook,
  ]);

  return contents;
}

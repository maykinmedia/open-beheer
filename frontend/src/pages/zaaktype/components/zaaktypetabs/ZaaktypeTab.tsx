import {
  AttributeGrid,
  Column,
  Field,
  FieldSet,
  Grid,
  Option,
  Sidebar,
  Toolbar,
  TypedField,
  fields2TypedFields,
  getFieldName,
  isPrimitive,
  useDialog,
} from "@maykin-ui/admin-ui";
import { slugify, string2Title } from "@maykin-ui/client-common";
import { invariant } from "@maykin-ui/client-common/assert";
import React, {
  JSX,
  ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useLoaderData, useLocation, useParams } from "react-router";
import { ArchiveForm } from "~/components";
import {
  RelatedObjectBadge,
  RelatedObjectDataGrid,
  RelatedObjectDataGridAction,
  RelatedObjectRenderer,
  getObjectValue,
} from "~/components/related";
import { useErrors } from "~/hooks";
import { useHashParam } from "~/hooks/useHashParam.ts";
import {
  AttributeGridSection,
  DataGridSection,
  DataGridTabConfig,
  TabConfig,
  TargetType,
  ZaaktypeLoaderData,
} from "~/pages";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { Expand, ExpandItemKeys, RelatedObject, components } from "~/types";

type ZaaktypeTabProps = {
  object: TargetType;
  tabConfig: TabConfig<TargetType>;
  onChange: React.ChangeEventHandler;
  onTabActionsChange: (
    tabConfig: TabConfig<TargetType>,
    actions: ZaaktypeAction[],
  ) => void;
};

type ResultaatType = components["schemas"]["ResultaatTypeWithUUID"];

/**
 * Renders a single tab, optionally containing different (vertical) section.
 * FIXME: INITIAL VALUES FOR HOOK MODAL
 */
export const ZaaktypeTab = ({
  object,
  tabConfig,
  onChange,
  onTabActionsChange,
}: ZaaktypeTabProps) => {
  const { fields } = useLoaderData() as ZaaktypeLoaderData;
  const location = useLocation();
  const { serviceSlug } = useParams();
  invariant(serviceSlug, "serviceSlug must be provided!");

  const isEditing =
    new URLSearchParams(location.search).get("editing") === "true";
  const errors = useErrors();

  // (Vertical) section data.
  const [sectionHash, setSectionHash] = useHashParam("section", "0");
  const activeSectionIndex = parseInt(sectionHash || "0");

  // The active (vertical) section.
  const activeSectionConfig = useMemo(() => {
    return tabConfig.sections[activeSectionIndex] || tabConfig.sections[0];
  }, [tabConfig, activeSectionIndex]);

  // Whether (vertical) sections exist within the tab.
  const doesActiveTabHaveMultipleSubTabs = useMemo(() => {
    return tabConfig.sections.length > 1;
  }, [tabConfig]);

  // Related object dialog.
  const hookDialog = useDialog();
  const [hookDialogState, setHookDialogState] = useState<{
    open: boolean;
    title?: string;
    body?: JSX.Element;
  }>();

  useEffect(() => {
    if (!hookDialogState) return;
    hookDialog(hookDialogState.title || "", hookDialogState.body, undefined, {
      open: hookDialogState.open,
    });
  }, [hookDialogState]);

  /**
   * Memoizes a version of the result relatedObject where complex fields
   * are replaced by React nodes rendering their data.
   *
   * @see `ZaaktypePage.handleChange`: this converts an object to string for
   *  presentation/editing. This operation is inverted by the change handler.
   * @returns A shallow copy of `result` with expanded fields replaced
   */
  const complexOverrides = useMemo(() => {
    const overrides: Partial<Record<keyof TargetType, ReactNode>> = {};

    for (const field of fields) {
      const _fieldName = field.name.split(".").pop();
      if (!_fieldName || !(_fieldName in object)) {
        continue;
      }

      const fieldName = _fieldName as keyof TargetType;
      const originalValue = object[fieldName];

      // Show object values.
      if (
        originalValue &&
        !isPrimitive(originalValue) &&
        !Array.isArray(originalValue)
      ) {
        overrides[fieldName] = isEditing ? (
          getObjectValue(originalValue)
        ) : (
          <RelatedObjectBadge relatedObject={originalValue} />
        );
      }
    }

    return overrides;
  }, [fields, object]);

  /**
   * FIXME: Only used for AttributeGrid, refactor.
   *
   * Memoizes a version of the result relatedObject where expandable fields
   * are replaced by React nodes rendering related data.
   *
   * @returns A shallow copy of `result` with expanded fields replaced
   */
  const expandedOverrides = useMemo(() => {
    if (!object || !object._expand) return {};

    const overrides: Partial<Record<keyof TargetType, ReactNode>> = {};

    for (const field of fields) {
      const fieldName = field.name.split(".").pop() as keyof TargetType;
      const originalValue = object[fieldName];
      const expand = object._expand;

      // Skip if the field is not expandable or has no value.
      if (!(fieldName in expand) || originalValue === null) {
        continue;
      }
      const relatedObject = expand[fieldName as keyof Expand<TargetType>];

      // Related fields that are directly editable should not be in overrides.
      if (isEditing && field.options) {
        continue;
      }

      overrides[fieldName] = (
        <RelatedObjectRenderer
          expandFields={fields2TypedFields(
            (activeSectionConfig.expandFields || []) as Field[],
          )}
          object={object}
          relatedObject={relatedObject as RelatedObject<TargetType>}
          relatedObjectKey={fieldName as ExpandItemKeys<TargetType>}
          fields={fields2TypedFields(fields as Field[])}
        />
      );
    }

    return overrides;
  }, [object, fields, tabConfig, activeSectionConfig]);

  /**
   * Gets called when the (vertical) section is changed.
   */
  const handleSectionChange = useCallback(
    (index: number) => {
      setSectionHash(index.toString());
    },
    [setSectionHash],
  );

  /**
   * Handles a list of data grid actions triggered by user mutations
   * in a `<RelatedObjectDataGrid>`. Each action (create, update, delete)
   * is transformed into a corresponding `ZaaktypeAction` and passed to
   * `onTabActionsChange` for submission to the backend.
   *
   * @param actions - The list of actions representing changes made in the related object grid.
   *
   * Notes:
   * - The object must have a defined `uuid` (enforced via invariant).
   * - Each action is mapped to a backend-persistable `ZaaktypeAction` with
   *   contextual data (`serviceSlug`, `zaaktypeUuid`, `relatedObjectKey`).
   * - Throws an error if an unknown action type is encountered.
   */
  const handleActionsChange = useCallback(
    (actions: RelatedObjectDataGridAction<RelatedObject<TargetType>>[]) => {
      const _tabConfig = tabConfig as DataGridTabConfig<TargetType>;
      invariant(object.uuid, "Zaaktype must have uuid set!");

      const zaaktypeActions: ZaaktypeAction[] = actions.map((action) => {
        const payloadBase = {
          serviceSlug: serviceSlug,
          zaaktypeUuid: object.uuid!,
          relatedObjectKey: _tabConfig.key,
        };

        switch (action.type) {
          case "CREATE":
            return {
              type: "ADD_RELATED_OBJECT",
              payload: {
                ...payloadBase,
                relatedObject: action.payload,
              },
            };
          case "UPDATE":
            return {
              type: "EDIT_RELATED_OBJECT",
              payload: {
                ...payloadBase,
                relatedObject: action.payload,
              },
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
            // @ts-expect-error - should not happen.
            throw new Error("Unknown action type: " + action.type);
        }
      });
      onTabActionsChange(tabConfig, zaaktypeActions);
    },
    [tabConfig, object, onTabActionsChange],
  );

  /**
   * Hook that allows modifying the `relatedObject` before committing changes.
   *
   * This function is called right before a change is committed, giving you a chance
   * to adjust or validate the `relatedObject`.
   *
   * @param relatedObject - The object related to the pending change.
   * @param actionType - The type of action describing the change.
   * @param relatedObjectKey - The key in the expanded target object corresponding to this related object.
   * @returns A promise resolving to either:
   * - The modified `relatedObject`, which will be committed.
   * - `false`, to cancel (skip) committing the change.
   *
   * If `false` is returned, the change will be discarded and not persisted.
   * If an updated object is returned, it will replace the original during commit.
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
   * Hook that handles pre-commit validation or enrichment for a `ResultaatType` object.
   *
   * This function is triggered before committing a change related to a `ResultaatType`,
   * allowing user interaction or automated adjustment of the object.
   *
   * If the action type indicates a delete operation, no additional processing is required,
   * and the original `ResultaatType` is returned immediately.
   *
   * For other action types, this hook opens a dialog (via `setHookDialogState`) presenting
   * an `ArchiveForm`. The user can complete the form to provide or modify
   * the `brondatumArchiefProcedure` field before the object is committed.
   *
   * @param resultaatType - The `ResultaatType` object to modify or validate.
   * @param actionType - The action type describing the pending operation (e.g., "CREATE", "UPDATE", "DELETE").
   * @param relatedObjectKey - The key in the expanded target object corresponding to this related object.
   * @returns A promise resolving to one of:
   * - The updated `ResultaatType` (if the user completes the form).
   * - The original `ResultaatType` (for delete actions).
   * - `false`, if the user cancels the dialog or an error occurs, indicating that the change should be skipped.
   */
  const resultaatTypeHook = useCallback(
    async (
      resultaatType: ResultaatType,
      actionType: RelatedObjectDataGridAction<ResultaatType>["type"],
    ): Promise<ResultaatType | false> => {
      // Delete requires no further actions.
      if (actionType.toUpperCase().includes("DELETE")) return resultaatType;
      return new Promise((resolve, reject) => {
        // Locate selectielijstklasse (resultaat) options
        const selectielijstklasseOptions = fields.find(
          (field) =>
            field.name === "_expand.resultaattypen.selectielijstklasse",
        )?.options as Option[] | undefined;

        // Throw if options can't be found.
        invariant(
          selectielijstklasseOptions,
          "Failed to locate selectielijstklasse field!",
        );

        // Update dialog state in order to render form
        setHookDialogState({
          open: true,
          title: string2Title(tabConfig.label),
          body: (
            <ArchiveForm
              resultaatType={resultaatType}
              selectielijstklasseOptions={selectielijstklasseOptions}
              // User completes resultaattype.
              onSubmit={({
                selectielijstklasse,
                brondatumArchiefProcedure,
              }) => {
                setHookDialogState({ open: false });

                // Resolve the resultaattype omschrijving field.
                const resultaatTypeOmschrijvingField = fields.find(
                  (f) =>
                    f.name ===
                    "_expand.resultaattypen.resultaattypeomschrijving",
                );

                // A default `resultaattypeomschrijving` value based on `brondatumArchiefProcedure.afleidingswijze`.
                // Use only when adding resultaattype.
                const defaultResultaatTypeOmschrijving =
                  actionType === "CREATE"
                    ? (resultaatTypeOmschrijvingField?.options?.find(
                        ({ label }) =>
                          label.toLowerCase() ===
                          brondatumArchiefProcedure.afleidingswijze.toLowerCase(),
                      )?.value as string | undefined)
                    : undefined;

                // Resolve with provided additions.
                resolve({
                  ...resultaatType,
                  selectielijstklasse,
                  resultaattypeomschrijving:
                    defaultResultaatTypeOmschrijving ||
                    resultaatType.resultaattypeomschrijving,
                  brondatum_archiefprocedure: brondatumArchiefProcedure, // FIXME: camelCase not accepted by BFF/OZ.
                } as ResultaatType);
              }}
              // User or system closes the modal, possibly due to an error
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
   * The <AttributeGrid/> with the data for the current tab/section.
   */
  const contents = useMemo(() => {
    if (tabConfig.view === "DataGrid") {
      const key = tabConfig.key;
      const relatedObjects = object._expand[key] || [];
      invariant(
        Array.isArray(relatedObjects),
        "relatedObjects must be an Array for RelatedObjectDataGrid!",
      );

      // The fields included in the fieldset.
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
    }

    if (isAttributeGridSection(tabConfig.view, activeSectionConfig)) {
      const fieldsets = activeSectionConfig.fieldsets.map((fieldset) => [
        fieldset[0],
        {
          ...fieldset[1],
          fields: fieldset[1].fields.map((fieldsetField) => {
            const field = fields.find((field) => field.name === fieldsetField);
            const editable =
              field?.name && field.name in expandedOverrides
                ? false
                : field?.editable;
            return { ...field, editable };
          }),
        },
      ]) as FieldSet<TargetType>[];

      return (
        <AttributeGrid
          object={
            {
              ...object,
              ...complexOverrides,
              ...expandedOverrides,
            } as TargetType
          }
          editable={isEditing ? undefined : false} // When in edit mode, allow fields to defined editable state, prevent editing otherwise.
          editing={isEditing}
          errors={errors}
          fieldsets={fieldsets}
          onChange={onChange}
        />
      );
    }

    return expandedOverrides[activeSectionConfig.key];
  }, [
    tabConfig.view,
    activeSectionConfig,
    object,
    expandedOverrides,
    isEditing,
    handleActionsChange,
    relatedObjectHook,
    onChange,
  ]);

  return doesActiveTabHaveMultipleSubTabs ? (
    <Grid>
      <Column span={2}>
        <Sidebar
          border={false}
          expandable={false}
          minWidth={false}
          sticky={false}
        >
          <Toolbar
            align="start"
            direction="vertical"
            items={tabConfig.sections.map((subTabConfig, index: number) => ({
              active: activeSectionIndex === index,
              children: (
                <>
                  {subTabConfig.icon}
                  {subTabConfig.label}
                </>
              ),
              key: slugify(subTabConfig.label),
              onClick: () => {
                handleSectionChange(index);
              },
            }))}
            variant="transparent"
          />
        </Sidebar>
      </Column>

      <Column span={10}>{contents}</Column>
    </Grid>
  ) : (
    contents
  );
};

/**
 * Returns whether view === "AttributeGrid", doubles as typeguard for `tabConfigSection`.
 */
const isAttributeGridSection = (
  view: string,
  // @ts-expect-error - TypeScript unhappy with unused, but necessary for type guard
  tabConfigSection: AttributeGridSection<TargetType> | DataGridSection,
): tabConfigSection is AttributeGridSection<TargetType> =>
  view === "AttributeGrid";

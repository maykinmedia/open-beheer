import { ErrorMessage, Tab, Tabs, getFieldName } from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Errors, useErrors } from "~/hooks";
import { useHashParam } from "~/hooks/useHashParam.ts";
import { useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import { TabConfig, TargetType } from "~/pages";
import {
  ZaaktypeAttributeGridTab,
  ZaaktypeDataGridTab,
} from "~/pages/zaaktype/components";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { Expanded, RelatedObject } from "~/types";

type ZaaktypeTabsProps = {
  object: TargetType;
  tabConfigs: TabConfig<TargetType>[];
  onChange: React.ChangeEventHandler;
  onTabActionsChange: (
    tabConfig: TabConfig<TargetType>,
    actions: ZaaktypeAction[],
  ) => void;
};

type FieldErrorsByTab = NonRelatedFieldErrorsByTab | RelatedFieldErrorsByTab;

type RelatedFieldErrorsByTab = Partial<{
  [index: string]: RelatedErrors;
}>;

type NonRelatedFieldErrorsByTab = Partial<{
  [index: string]: NonRelatedErrors;
}>;

type NonFieldErrorsByTab = Partial<{
  [index in keyof TargetType]: string;
}>;

type RelatedErrors = Errors<Expanded<TargetType>>[];

type NonRelatedErrors = Errors<TargetType>;

/**
 * Renders the tabs for a zaaktype
 */
export function ZaaktypeTabs({
  object,
  tabConfigs,
  onChange,
  onTabActionsChange,
}: ZaaktypeTabsProps) {
  //
  // Error handling.
  //

  // Get raw action/errors tuple[].
  const errorTuples = useErrors<
    TargetType | RelatedObject<TargetType>,
    ZaaktypeAction
  >(undefined, false);

  // Create a record that matches every relatedObjectKey/tabKey with a non-field error string.
  const nonFieldErrorsByTab = useMemo<NonFieldErrorsByTab>(() => {
    return errorTuples.reduce<NonFieldErrorsByTab>((acc, [, errors]) => {
      // Search for errors based on tabConfig keys.
      // - Applicable to actions acting on entire ZaakType hierarchy (e.g. "PUBLISH_VERSION").
      // - Relevant for non-nested errors relating to directly to a relation.
      // - Action does not have a relatedObjectKey.
      // - Errors relate to relation expressed by tab, not to nested fields.
      tabConfigs.forEach((tabConfig) => {
        const _key = tabConfig.key;
        if (_key in errors) {
          // `key` is in errors therefore is must be.
          const key = _key as keyof (TargetType | RelatedObject<TargetType>);
          acc[key] = errors[key];
        }
      });
      return acc;
    }, {});
  }, [errorTuples]);

  /**
   * Return `Errors[]` of `size`, each object sits position indicated `ZaaktypeAction` found in
   * `errorTuples[number][0].payload.rowIndex`.
   */
  const errorPerRow = useCallback(
    (
      errorTuples: [ZaaktypeAction, Errors<RelatedObject<TargetType>>][],
      size: number,
    ): Errors<TargetType>[] => {
      return errorTuples.reduce((acc, [action, errors]) => {
        if (!action || !action.payload || !("rowIndex" in action.payload))
          return acc;

        acc[action.payload.rowIndex] = errors;
        return acc;
      }, new Array(size).fill({}));
    },
    [],
  );

  // Create a record that matches every relatedObjectKey/tabKey with an `Errors[]` array.
  const fieldErrorsByTab = useMemo<FieldErrorsByTab>(
    () =>
      errorTuples.reduce((acc, [action, errors]) => {
        // Search for errors based on the relatedObjectKey in action payload
        // - Applicable to actions acting on related objects (e.g. "ADD_RELATED_OBJECT").
        // - Relevant for related objects in DataGrids.
        // - Action explicitly sets tab.
        // - Errors relate to fields within tab rather than relation expressed by tab.
        if ("relatedObjectKey" in action.payload) {
          const key = action.payload.relatedObjectKey;
          const relatedObject = object._expand[key];

          // For ZaaktypeDataGridTab, construct an Error[] based on each related object.
          if (relatedObject) {
            const length = Object.keys(relatedObject).length;

            const siblings = errorTuples.filter(([sAction]) => {
              return (
                "relatedObjectKey" in sAction.payload &&
                sAction.payload.relatedObjectKey === key
              );
            });

            return {
              ...acc,
              [key]: errorPerRow(siblings, length),
            };
          }
        }

        // Search for errors based on tabConfig keys.
        // - Applicable to actions acting on ZaakType (e.g. "UPDATE_VERSION").
        // - Relevant for errors on ZaakType fields.
        // - Errors relate to ZaakType fields directly.
        const _acc: NonRelatedFieldErrorsByTab = { ...acc };
        for (const tabConfig of tabConfigs) {
          if (tabConfig.view !== "AttributeGrid") continue;

          const key = tabConfig.key;
          const tabConfigFields = tabConfig.sections.flatMap((section) =>
            section.fieldsets.flatMap((fieldset) =>
              fieldset[1].fields.map((field) => getFieldName(field)),
            ),
          );

          for (const tabConfigField of tabConfigFields) {
            if (
              tabConfigField in object &&
              !Array.isArray(object[tabConfigField]) &&
              tabConfigField in errors
            ) {
              // `tabConfigField` is object and `object[tabConfigField]` is not an array.
              // also: `tabConfigField` is in errors, therefore it must be.
              const errs = errors as NonRelatedErrors;

              const current = _acc[key] ?? {};
              _acc[key] = {
                ...current,
                [tabConfigField]: errs[tabConfigField],
              };
            }
          }
        }
        return _acc;
      }, {}),
    [errorTuples, object, errorPerRow],
  );

  // Store NonFieldErrorsByTab record in state.
  const [nonFieldErrorsState, setNonFieldErrorsState] =
    useState<NonFieldErrorsByTab>(nonFieldErrorsByTab);

  // Sync FieldErrorsByTab record.
  useEffect(() => {
    // Only update, don't clear (automatically).
    // This prevents clearing errors on tab change.
    if (Object.keys(nonFieldErrorsByTab).length) {
      setNonFieldErrorsState(nonFieldErrorsByTab);
    }
  }, [nonFieldErrorsByTab]);

  // Store FieldErrorsByTab record in state.
  const [fieldErrorsState, setFieldErrorsState] =
    useState<FieldErrorsByTab>(fieldErrorsByTab);

  const relatedFieldErrorsByTab = useMemo<RelatedFieldErrorsByTab>(
    () =>
      Object.fromEntries(
        Object.entries(fieldErrorsState).filter(([, errors]) =>
          Array.isArray(errors),
        ),
      ),
    [fieldErrorsState, object],
  );

  const nonRelatedFieldErrorsByTab = useMemo<NonRelatedFieldErrorsByTab>(
    () =>
      Object.fromEntries(
        Object.entries(fieldErrorsState).map(([key, errors]) => [
          key,
          Object.fromEntries(
            Object.entries(errors).filter(([key]) => key in object),
          ),
        ]),
      ),
    [fieldErrorsState, object],
  );

  // Sync FieldErrorsByTab record.
  useEffect(() => {
    // Only update, don't clear (automatically).
    // This prevents clearing errors on tab change.
    if (Object.keys(fieldErrorsByTab).length) {
      setFieldErrorsState(fieldErrorsByTab);
    }
  }, [fieldErrorsByTab]);

  /**
   * Returns wrapped `fn` that clears `nonFieldErrorsState` and `fieldErrorsState` whenever called.
   * @param fn - The function to wrap.
   */
  // eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
  const clearErrorsOn = <T extends Function>(fn: T) => {
    return (...args: unknown[]) => {
      setNonFieldErrorsState({});
      setFieldErrorsState({});
      fn(...args);
    };
  };

  //
  // Regular hooks.
  //

  const submitAction = useSubmitAction(false);
  // (Horizontal) tab data.
  const [tabHash] = useHashParam("tab", "0");
  const activeTabIndex = parseInt(tabHash || "0");

  //
  // Events.
  //

  /**
   * Gets called when the (horizontal) tab is changed.
   */
  const handleTabChange = useCallback(
    (index: number) => {
      invariant(object.uuid, "object.uuid must be set");

      submitAction({
        type: "SET_TAB",
        payload: {
          uuid: object.uuid,
          tabIndex: index,
        },
      });
    },
    [object, submitAction],
  );

  //
  // Render.
  //

  const tabs = useMemo(
    () =>
      tabConfigs.map((tabConfig) => {
        // console.log(tabConfig.key, fieldErrorsState[tabConfig.key]);
        const content =
          tabConfig.view === "DataGrid" ? (
            <ZaaktypeDataGridTab
              errors={relatedFieldErrorsByTab[tabConfig.key] || []}
              object={object}
              tabConfig={tabConfig}
              onTabActionsChange={clearErrorsOn(onTabActionsChange)}
            />
          ) : (
            <ZaaktypeAttributeGridTab
              errors={nonRelatedFieldErrorsByTab[tabConfig.key] || {}}
              object={object}
              tabConfig={tabConfig}
              onChange={clearErrorsOn(onChange)}
            />
          );

        return (
          <Tab
            key={tabConfig.label}
            label={
              tabConfig.key in nonFieldErrorsState ||
              tabConfig.key in fieldErrorsState
                ? tabConfig.label + " (!)"
                : tabConfig.label
            }
          >
            {tabConfig.key in nonFieldErrorsState && (
              <ErrorMessage>
                {nonFieldErrorsState[tabConfig.key as keyof TargetType]}
              </ErrorMessage>
            )}
            {content}
          </Tab>
        );
      }),
    [tabConfigs, object, onChange, nonFieldErrorsState, fieldErrorsState],
  );

  return (
    <Tabs activeTabIndex={activeTabIndex} onTabChange={handleTabChange}>
      {tabs}
    </Tabs>
  );
}

import { ErrorMessage, Tab, Tabs } from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  useNonFieldErrors,
  useNonRelatedFieldErrors,
  useRelatedFieldErrors,
} from "~/hooks";
import { useHashParam } from "~/hooks/useHashParam.ts";
import { useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import { TabConfig, TargetType } from "~/pages";
import {
  ZaaktypeAttributeGridTab,
  ZaaktypeDataGridTab,
} from "~/pages/zaaktype/components";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";

type ZaaktypeTabsProps = {
  object: TargetType;
  tabConfigs: TabConfig<TargetType>[];
  onChange: React.ChangeEventHandler;
  onTabActionsChange: (
    tabConfig: TabConfig<TargetType>,
    actions: ZaaktypeAction[],
  ) => void;
};

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

  // Create a record that matches every relatedObjectKey/tabKey with a non-field error string.
  const nonFieldErrorsByTab = useNonFieldErrors(tabConfigs);

  // Create a record that matches every relatedObjectKey/tabKey with an `Errors[]` array.
  const relatedFieldErrorsByTab = useRelatedFieldErrors(object);

  // Create a record that matches every relatedObjectKey/tabKey with an `Errors[]` array.
  const nonRelatedFieldErrorsByTab = useNonRelatedFieldErrors(
    tabConfigs,
    object,
  );

  // Store NonFieldErrorsByTab record in state.
  const [nonFieldErrorsState, setNonFieldErrorsState] =
    useState(nonFieldErrorsByTab);

  // Sync FieldErrorsByTab record.
  useEffect(() => {
    // Only update, don't clear (automatically).
    // This prevents clearing errors on tab change.
    if (Object.keys(nonFieldErrorsByTab).length) {
      setNonFieldErrorsState(nonFieldErrorsByTab);
    }
  }, [nonFieldErrorsByTab]);

  // Store `relatedFieldErrorsByTab` record in state.
  const [relatedFieldErrorsByTabState, setRelatedFieldErrorsByTabState] =
    useState(relatedFieldErrorsByTab);

  // Sync `relatedFieldErrorsByTabState`.
  useEffect(() => {
    // Only update, don't clear (automatically).
    // This prevents clearing errors on tab change.
    if (Object.keys(relatedFieldErrorsByTab).length) {
      setRelatedFieldErrorsByTabState(relatedFieldErrorsByTab);
    }
  }, [relatedFieldErrorsByTab]);

  // Store `relatedFieldErrorsByTab` record in state.
  const [nonRelatedFieldErrorsByTabState, setNonRelatedFieldErrorsByTabState] =
    useState(nonRelatedFieldErrorsByTab);

  // Sync `nonRelatedFieldErrorsByTabState`.
  useEffect(() => {
    // Only update, don't clear (automatically).
    // This prevents clearing errors on tab change.
    if (Object.keys(nonRelatedFieldErrorsByTab).length) {
      setNonRelatedFieldErrorsByTabState(nonRelatedFieldErrorsByTab);
    }
  }, [nonRelatedFieldErrorsByTab]);

  /**
   * Returns wrapped `fn` that clears `nonFieldErrorsState` and `relatedFieldErrorsByTabState` whenever called.
   * @param fn - The function to wrap.
   */
  // eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
  const clearErrorsOn = <T extends Function>(fn: T) => {
    return (...args: unknown[]) => {
      setNonFieldErrorsState({});
      setRelatedFieldErrorsByTabState({});
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
        // console.log(tabConfig.key, relatedFieldErrorsByTabState[tabConfig.key]);
        const content =
          tabConfig.view === "DataGrid" ? (
            <ZaaktypeDataGridTab
              errors={relatedFieldErrorsByTabState[tabConfig.key] || []}
              object={object}
              tabConfig={tabConfig}
              onTabActionsChange={clearErrorsOn(onTabActionsChange)}
            />
          ) : (
            <ZaaktypeAttributeGridTab
              errors={nonRelatedFieldErrorsByTabState[tabConfig.key] || {}}
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
              tabConfig.key in relatedFieldErrorsByTabState ||
              tabConfig.key in nonRelatedFieldErrorsByTabState
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
    [
      tabConfigs,
      object,
      onChange,
      nonFieldErrorsState,
      relatedFieldErrorsByTabState,
    ],
  );

  return (
    <Tabs activeTabIndex={activeTabIndex} onTabChange={handleTabChange}>
      {tabs}
    </Tabs>
  );
}

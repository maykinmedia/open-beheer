import { ErrorMessage, Tab, Tabs } from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useErrors } from "~/hooks";
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
  const errors = useErrors<Record<string, string>>();
  const submitAction = useSubmitAction(false);
  // (Horizontal) tab data.
  const [tabHash] = useHashParam("tab", "0");
  const activeTabIndex = parseInt(tabHash || "0");

  const [errorsState, setErrorsState] =
    useState<Partial<Record<string, string>>>(errors);
  useEffect(() => {
    setErrorsState(errors);
  }, [errors]);

  /**
   * Returns wrapped `fn` that clears `setErrorsState` whenever called.
   * @param fn - The function to wrap.
   */
  // eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
  const clearErrorsOn = <T extends Function>(fn: T) => {
    return (...args: unknown[]) => {
      setErrorsState({});
      fn(...args);
    };
  };

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

  const tabs = useMemo(
    () =>
      tabConfigs.map((tabConfig) => {
        const content =
          tabConfig.view === "DataGrid" ? (
            <ZaaktypeDataGridTab
              object={object}
              tabConfig={tabConfig}
              onTabActionsChange={clearErrorsOn(onTabActionsChange)}
            />
          ) : (
            <ZaaktypeAttributeGridTab
              object={object}
              tabConfig={tabConfig}
              onChange={clearErrorsOn(onChange)}
            />
          );

        return (
          <Tab
            key={tabConfig.label}
            label={
              tabConfig.key in errorsState
                ? tabConfig.label + " (!)"
                : tabConfig.label
            }
          >
            {tabConfig.key in errorsState ? (
              <ErrorMessage>{errorsState[tabConfig.key]}</ErrorMessage>
            ) : undefined}
            {content}
          </Tab>
        );
      }),
    [tabConfigs, object, onChange, errorsState],
  );

  return (
    <Tabs activeTabIndex={activeTabIndex} onTabChange={handleTabChange}>
      {tabs}
    </Tabs>
  );
}

import { ErrorMessage, Tab, Tabs } from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import React, { useCallback, useMemo } from "react";
import { useErrorsState } from "~/hooks";
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
  // Hooks.
  //

  const [nonFieldErrors, relatedFieldErrorsByTab, nonRelatedFieldErrorsByTab] =
    useErrorsState<TargetType, ZaaktypeAction>(object, tabConfigs);

  const submitAction = useSubmitAction(false);
  // (Horizontal) tab data.
  const [tabHash] = useHashParam("tab", tabConfigs[0]?.key);
  const activeTabIndex = Math.max(
    tabConfigs.findIndex((t) => t.key === tabHash),
    0,
  );

  //
  // Events.
  //

  /**
   * Gets called when the (horizontal) tab is changed.
   */
  const handleTabChange = useCallback(
    (index: number) => {
      const key = tabConfigs[index].key;
      invariant(object.uuid, "object.uuid must be set");

      submitAction({
        type: "SET_TAB",
        payload: {
          uuid: object.uuid,
          tabKey: key,
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
          tabConfig.view === "AttributeGrid" ? (
            <ZaaktypeAttributeGridTab
              errors={nonRelatedFieldErrorsByTab[tabConfig.key] || {}}
              object={object}
              tabConfig={tabConfig}
              onChange={onChange}
            />
          ) : (
            <ZaaktypeDataGridTab
              errors={relatedFieldErrorsByTab[tabConfig.key] || []}
              object={object}
              tabConfig={tabConfig}
              onTabActionsChange={onTabActionsChange}
            />
          );

        return (
          <Tab
            key={tabConfig.label}
            label={
              tabConfig.key in nonFieldErrors ||
              tabConfig.key in relatedFieldErrorsByTab ||
              tabConfig.key in nonRelatedFieldErrorsByTab
                ? tabConfig.label + " (!)"
                : tabConfig.label
            }
          >
            {tabConfig.key in nonFieldErrors && (
              <ErrorMessage>
                {nonFieldErrors[tabConfig.key as keyof TargetType]}
              </ErrorMessage>
            )}
            {content}
          </Tab>
        );
      }),
    [
      tabConfigs,
      object,
      nonFieldErrors,
      relatedFieldErrorsByTab,
      nonRelatedFieldErrorsByTab,
      onChange,
      onTabActionsChange,
    ],
  );

  return (
    <Tabs activeTabIndex={activeTabIndex} onTabChange={handleTabChange}>
      {tabs}
    </Tabs>
  );
}

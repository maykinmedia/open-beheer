import { Tab, Tabs } from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import React, { useCallback, useMemo } from "react";
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
  const submitAction = useSubmitAction(false);

  // (Horizontal) tab data.
  const [tabHash] = useHashParam("tab", "0");
  const activeTabIndex = parseInt(tabHash || "0");

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
              onTabActionsChange={onTabActionsChange}
            />
          ) : (
            <ZaaktypeAttributeGridTab
              object={object}
              tabConfig={tabConfig}
              onChange={onChange}
            />
          );

        return (
          <Tab key={tabConfig.label} label={tabConfig.label}>
            {content}
          </Tab>
        );
      }),
    [tabConfigs, object, onChange],
  );

  return (
    <Tabs activeTabIndex={activeTabIndex} onTabChange={handleTabChange}>
      {tabs}
    </Tabs>
  );
}

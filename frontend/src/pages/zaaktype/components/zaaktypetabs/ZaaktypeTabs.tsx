import { Tab, Tabs } from "@maykin-ui/admin-ui";
import React, { useCallback, useMemo } from "react";
import { useHashParam } from "~/hooks/useHashParam.ts";
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
  // (Horizontal) tab data.
  const [tabHash, setTabHash] = useHashParam("tab", "0");
  const activeTabIndex = parseInt(tabHash || "0");

  // (Vertical) section data.
  const [, setSectionHash] = useHashParam("section", "0");

  /**
   * Gets called when the (horizontal) tab is changed.
   */
  const handleTabChange = useCallback(
    (index: number) => {
      setTabHash(index.toString());
      setSectionHash("0");
    },
    [setTabHash, setSectionHash],
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

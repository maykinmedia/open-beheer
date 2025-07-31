import {
  AttributeGrid,
  Body,
  Button,
  CardBaseTemplate,
  Column,
  Grid,
  H2,
  Sidebar,
  Solid,
  Tab,
  Tabs,
  Toolbar,
} from "@maykin-ui/admin-ui";
import { slugify, ucFirst } from "@maykin-ui/client-common";
import { invariant } from "@maykin-ui/client-common/assert";
import { ReactNode, useCallback, useMemo } from "react";
import { useLoaderData, useParams } from "react-router";
import { VersionSelector } from "~/components/VersionSelector";
import { RelatedObjectRenderer } from "~/components/related";
import { useBreadcrumbItems, useCombinedSearchParams } from "~/hooks";
import { useHashParam } from "~/hooks/useHashParam.ts";
import { useSubmitAction } from "~/hooks/useSubmitAction.ts";
import { getZaaktypeUUID } from "~/lib";
import {
  AttributeGridSection,
  DataGridSection,
  TABS_CONFIG_ALGEMEEN,
  TABS_CONFIG_DOCUMENTTYPEN,
  TABS_CONFIG_EIGENSCHAPPEN,
  TABS_CONFIG_OVERVIEW,
  TABS_CONFIG_RELATIES,
  TABS_CONFIG_ROLTYPEN,
  TABS_CONFIG_STATUSTYPEN,
  TabConfig,
  TargetType,
  ZaaktypeLoaderData,
} from "~/pages";
import { TABS_CONFIG_OBJECTTYPEN } from "~/pages/zaaktype/tabs/objecttypen.tsx";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { Expand } from "~/types";

export const TABS_CONFIG: TabConfig<TargetType>[] = [
  TABS_CONFIG_OVERVIEW,
  TABS_CONFIG_ALGEMEEN,
  TABS_CONFIG_STATUSTYPEN,
  TABS_CONFIG_OBJECTTYPEN,
  TABS_CONFIG_DOCUMENTTYPEN,
  TABS_CONFIG_ROLTYPEN,
  TABS_CONFIG_EIGENSCHAPPEN,
  TABS_CONFIG_RELATIES,
];

/**
 * Renders the detail view for a single zaaktype, with tabs for attributes and related data.
 */
export function ZaaktypePage() {
  const { result, versions } = useLoaderData() as ZaaktypeLoaderData;

  const breadcrumbItems = useBreadcrumbItems();
  const submitAction = useSubmitAction<ZaaktypeAction>();

  return (
    <CardBaseTemplate
      breadcrumbItems={breadcrumbItems}
      cardProps={{
        justify: "space-between",
      }}
    >
      <Body fullHeight>
        <H2>
          {ucFirst(result.identificatie ?? "")}{" "}
          {result.omschrijving ? `(${result.omschrijving})` : null}
        </H2>

        {versions && (
          <VersionSelector
            selectedVersionUUID={getZaaktypeUUID(result)}
            versions={versions}
            onVersionChange={({ uuid }) =>
              submitAction({
                type: "SELECT_VERSION",
                payload: { uuid },
              })
            }
          />
        )}

        <ZaaktypeTabs />
      </Body>

      <ZaaktypeToolbar />
    </CardBaseTemplate>
  );
}

/**
 * Renders the tabs for a zaaktype
 */
function ZaaktypeTabs() {
  const { fields, result } = useLoaderData() as ZaaktypeLoaderData;

  // (Horizontal) tab data.
  const [tabHash, setTabHash] = useHashParam("tab", "0");
  const activeTabIndex = parseInt(tabHash);

  // (Vertical) section data.
  const [sectionHash, setSectionHash] = useHashParam("section", "0");
  const activeSectionIndex = parseInt(sectionHash);

  // The active (vertical) section.
  const activeSectionConfig = useMemo(() => {
    return TABS_CONFIG[activeTabIndex].sections[activeSectionIndex];
  }, [activeTabIndex, activeSectionIndex]);

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

  /**
   * Memoizes a version of the result object where expandable fields
   * are replaced by React nodes rendering related data.
   *
   * @returns A shallow copy of `result` with expanded fields replaced
   */
  const serializedResult = useMemo(() => {
    if (!result || !result._expand) return {};

    const overrides: Partial<Record<keyof TargetType, ReactNode>> = {};

    for (const field of fields) {
      const fieldName = field.name as keyof TargetType;
      const originalValue = result[fieldName];
      const expand = result._expand;

      // Skip if the field is not expandable or has no value.
      if (!(fieldName in expand) || originalValue === null) continue;

      overrides[fieldName] = (
        <RelatedObjectRenderer
          expandFields={activeSectionConfig.expandFields}
          field={fieldName as keyof Expand<typeof result>}
          object={result}
          view={TABS_CONFIG[activeTabIndex].view}
        />
      );
    }

    return overrides;
    // TODO: Optimize this by inspecting if the field is part of the active tab.
  }, [fields, result, activeTabIndex]);

  const tabs = useMemo(
    () =>
      TABS_CONFIG.map((tabConfig) => (
        <Tab key={tabConfig.label} label={tabConfig.label}>
          <ZaaktypeTab
            view={tabConfig.view}
            expandedOverrides={serializedResult}
            tabConfig={tabConfig}
            tabConfigSection={activeSectionConfig}
          />
        </Tab>
      )),
    [result, serializedResult, activeSectionIndex],
  );

  return (
    <Tabs activeTabIndex={activeTabIndex} onTabChange={handleTabChange}>
      {tabs}
    </Tabs>
  );
}

/**
 * Renders a single tab, optionally containing different (vertical) section.
 */
const ZaaktypeTab = ({
  tabConfig,
  tabConfigSection,
  view,
  expandedOverrides,
}: ZaaktypeTabProps) => {
  const { result } = useLoaderData() as ZaaktypeLoaderData;

  // (Horizontal) tab data.
  const [tabHash] = useHashParam("tab", "0");
  const activeTabIndex = parseInt(tabHash);

  // (Vertical) section data.
  const [sectionHash, setSectionHash] = useHashParam("section", "0");
  const activeSectionIndex = parseInt(sectionHash);

  // Whether (vertical) sections exist within the tab.
  const doesActiveTabHaveMultipleSubTabs = useMemo(() => {
    return TABS_CONFIG[activeTabIndex].sections.length > 1;
  }, [activeTabIndex]);

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
   * The <AttributeGrid/> with the data for the current tab/section.
   */
  const contents = useMemo(() => {
    if (isAttributeGridSection(view, tabConfigSection)) {
      return (
        <AttributeGrid
          object={{ ...result, ...expandedOverrides } as TargetType}
          fieldsets={tabConfigSection.fieldsets}
        />
      );
    }

    return expandedOverrides[tabConfigSection.key];
  }, [view, tabConfigSection, result, expandedOverrides]);

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

type ZaaktypeTabProps = {
  tabConfig: TabConfig<TargetType>;
  tabConfigSection:
    | AttributeGridSection<TargetType>
    | DataGridSection<TargetType>;
  view: "AttributeGrid" | "DataGrid";
  expandedOverrides: Partial<Record<keyof TargetType, ReactNode>>;
};

/**
 * Renders the bottom toolbar containing (primary) actions.
 */
function ZaaktypeToolbar() {
  const [, setCombinedSearchParams] = useCombinedSearchParams();
  const { serviceSlug } = useParams();
  invariant(serviceSlug, "serviceSlug must be provided!");

  return (
    <Toolbar align="end" pad variant="alt" sticky={"bottom"}>
      <Button
        variant="primary"
        onClick={() => setCombinedSearchParams({ editing: "true" })}
      >
        <Solid.PencilSquareIcon />
        Bewerken
      </Button>
    </Toolbar>
  );
}

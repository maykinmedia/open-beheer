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
import { ReactNode, useCallback, useMemo } from "react";
import { useLoaderData, useParams } from "react-router";
import { VersionSelector } from "~/components/VersionSelector";
import { RelatedObjectRenderer } from "~/components/related";
import { useBreadcrumbItems } from "~/hooks";
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
  const { fields, result, versions } = useLoaderData() as ZaaktypeLoaderData;

  const { serviceSlug } = useParams();
  const breadcrumbItems = useBreadcrumbItems();
  const [tabHash, setTabHash] = useHashParam("tab", "0");
  const [sectionHash, setSectionHash] = useHashParam("section", "0");
  const submitAction = useSubmitAction<ZaaktypeAction>();

  const activeTabIndex = parseInt(tabHash);
  const activeSectionIndex = parseInt(sectionHash);

  const activeSectionConfig = useMemo(() => {
    return TABS_CONFIG[activeTabIndex].sections[activeSectionIndex];
  }, [activeTabIndex, activeSectionIndex]);

  const doesActiveTabHaveMultipleSubTabs = useMemo(() => {
    return TABS_CONFIG[activeTabIndex].sections.length > 1;
  }, [activeTabIndex]);

  const handleTabChange = useCallback(
    (index: number) => {
      setTabHash(index.toString());
      setSectionHash("0");
    },
    [setTabHash, setSectionHash],
  );

  const handleSectionChange = useCallback(
    (index: number) => {
      setSectionHash(index.toString());
    },
    [setSectionHash],
  );

  /**
   * Memoizes a version of the result object where expandable fields
   * are replaced by React nodes rendering related data.
   *
   * @returns A shallow copy of `result` with expanded fields replaced
   */
  const expandedOverrides = useMemo(() => {
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

  /**
   * Memoizes the title.
   */
  const displayTitle = useMemo(() => {
    const id = result.identificatie ?? "";
    return ucFirst(id);
  }, [result.identificatie]);

  /**
   * Memoizes the the rendered tabs.
   */
  const renderedTabs = useMemo(() => {
    return TABS_CONFIG.map((tabConfig) => ({
      label: tabConfig.label,
      element: (
        <>
          {doesActiveTabHaveMultipleSubTabs ? (
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
                    items={tabConfig.sections.map(
                      (subTabConfig, index: number) => ({
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
                      }),
                    )}
                    variant="transparent"
                  />
                </Sidebar>
              </Column>
              <Column span={10}>
                <ZaaktypeTab
                  view={tabConfig.view}
                  expandedOverrides={expandedOverrides}
                  result={result}
                  tabConfigSection={activeSectionConfig}
                />
              </Column>
            </Grid>
          ) : (
            <ZaaktypeTab
              view={tabConfig.view}
              expandedOverrides={expandedOverrides}
              result={result}
              tabConfigSection={tabConfig.sections[0]}
            />
          )}
        </>
      ),
    }));
  }, [result, expandedOverrides, activeSectionIndex]);

  return (
    <CardBaseTemplate
      breadcrumbItems={breadcrumbItems}
      cardProps={{
        justify: "space-between",
      }}
    >
      <Body fullHeight>
        <H2>
          {displayTitle}{" "}
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
        <Tabs activeTabIndex={activeTabIndex} onTabChange={handleTabChange}>
          {renderedTabs.map(({ label, element }) => (
            <Tab key={label} label={label}>
              {element}
            </Tab>
          ))}
        </Tabs>
      </Body>

      <Toolbar align="end" pad variant="alt" sticky={"bottom"}>
        {serviceSlug && (
          <Button
            variant="primary"
            onClick={() =>
              submitAction({
                type: "CREATE_VERSION",
                payload: { serviceSlug: serviceSlug, zaaktype: result },
              })
            }
          >
            <Solid.PlusIcon />
            Nieuwe versie
          </Button>
        )}
      </Toolbar>
    </CardBaseTemplate>
  );
}

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
  tabConfigSection:
    | AttributeGridSection<TargetType>
    | DataGridSection<TargetType>;
  view: "AttributeGrid" | "DataGrid";
  result: TargetType;
  expandedOverrides: Partial<Record<keyof TargetType, ReactNode>>;
};

/**
 * Renders a single tab
 */
const ZaaktypeTab = ({
  tabConfigSection,
  view,
  result,
  expandedOverrides,
}: ZaaktypeTabProps) => {
  if (isAttributeGridSection(view, tabConfigSection)) {
    return (
      <AttributeGrid
        object={{ ...result, ...expandedOverrides } as TargetType}
        fieldsets={tabConfigSection.fieldsets}
      />
    );
  }

  return expandedOverrides[tabConfigSection.key];
};

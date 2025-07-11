import {
  AttributeGrid,
  Badge,
  Body,
  CardBaseTemplate,
  Column,
  DataGrid,
  Grid,
  H2,
  P,
  Primitive,
  Sidebar,
  Tab,
  Tabs,
  Toolbar,
} from "@maykin-ui/admin-ui";
import { slugify, ucFirst } from "@maykin-ui/client-common";
import { ReactNode, useCallback, useMemo, useState } from "react";
import { useLoaderData, useNavigate } from "react-router";
import { VersionSelector } from "~/components/VersionSelector";
import { useBreadcrumbItems } from "~/hooks";
import { getZaaktypeUUID, isPrimitive } from "~/lib";
import {
  ExpandItemKeys,
  LeafTabConfig,
  NestedTabConfig,
  TABS_CONFIG_ALGEMEEN,
  TABS_CONFIG_DOCUMENTTYPEN,
  TABS_CONFIG_EIGENSCHAPPEN,
  TABS_CONFIG_OVERVIEW,
  TABS_CONFIG_RELATIES,
  TABS_CONFIG_ROLTYPEN,
  TABS_CONFIG_STATUSTYPEN,
  TargetType,
  ZaaktypeLoaderData,
} from "~/pages";
import { TABS_CONFIG_OBJECTTYPEN } from "~/pages/zaaktype/tabs/objecttypen.tsx";
import { components } from "~/types";

export const TABS_CONFIG: NestedTabConfig<TargetType>[] = [
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
  const navigate = useNavigate();
  const breadcrumbItems = useBreadcrumbItems();
  const [activeTabIndex, setActiveTabIndex] = useState(0);
  const [activeSubTabIndex, setActiveSubTabIndex] = useState(0);

  const activeSubTabConfig = useMemo(() => {
    return TABS_CONFIG[activeTabIndex].tabs[activeSubTabIndex];
  }, [activeTabIndex, activeSubTabIndex]);
  const doesActiveTabHaveMultipleSubTabs = useMemo(() => {
    return TABS_CONFIG[activeTabIndex].tabs.length > 1;
  }, [activeTabIndex]);

  const { fields, result, versions } = useLoaderData() as ZaaktypeLoaderData;

  const handleTabChange = useCallback(
    (index: number) => {
      setActiveTabIndex(index);
      setActiveSubTabIndex(0); // Reset sub-tab index when changing main tab
    },
    [setActiveTabIndex, setActiveSubTabIndex],
  );

  const handleSubTabChange = useCallback(
    (index: number) => {
      setActiveSubTabIndex(index);
    },
    [setActiveSubTabIndex],
  );

  /**
   * Extracts an array of related objects from the expansion map.
   *
   * @param expand - The `_expand` map from loader data
   * @param field - The name of the field to extract from `expand`
   * @returns An array of related objects, or empty if none
   */
  function extractRelatedObjects(
    expand: ZaaktypeLoaderData["result"]["_expand"],
    field: keyof ZaaktypeLoaderData["result"],
  ): Record<ExpandItemKeys, Primitive | object>[] {
    const value = expand?.[field as keyof typeof expand];
    if (!Array.isArray(value)) {
      console.error(
        `Expected an array for field "${field}" in _expand, but got:`,
        value,
      );
      return [];
    }
    return value as Record<ExpandItemKeys, Primitive | object>[];
  }

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

      const relatedObjects = extractRelatedObjects(expand, fieldName);
      // Skip if no related objects are found.
      if (!relatedObjects.length) continue;

      overrides[fieldName] = (
        <RelatedObjectRenderer
          relatedObjects={relatedObjects}
          config={activeSubTabConfig}
        />
      );
    }

    return overrides;
    // TODO: Optimize this by inspecting if the field is part of the active tab.
  }, [fields, result, activeTabIndex]);

  /**
   * Navigate to the selected version of this zaaktype.
   *
   * @param version - The version selected by the user
   */
  const handleVersionChange = useCallback(
    (version: components["schemas"]["VersionSummary"]) => {
      navigate(`../${version.uuid}`);
    },
    [],
  );

  const displayTitle = useMemo(() => {
    const id = result.identificatie ?? "";
    return ucFirst(id);
  }, [result.identificatie]);

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
                    items={tabConfig.tabs.map((subTabConfig, index) => ({
                      active: activeSubTabIndex === index,
                      children: (
                        <P size="xs">
                          {subTabConfig.icon}
                          {"\u00A0\u00A0"}
                          {"\u00A0\u00A0"}
                          {subTabConfig.label}
                        </P>
                      ),
                      key: slugify(subTabConfig.label),
                      onClick: () => {
                        handleSubTabChange(index);
                      },
                    }))}
                    variant="transparent"
                  />
                </Sidebar>
              </Column>
              <Column span={10}>
                <ZaaktypeTab
                  expandedOverrides={expandedOverrides}
                  result={result}
                  tabConfig={activeSubTabConfig}
                />
              </Column>
            </Grid>
          ) : (
            <ZaaktypeTab
              expandedOverrides={expandedOverrides}
              result={result}
              tabConfig={tabConfig.tabs[0]}
            />
          )}
        </>
      ),
    }));
  }, [result, expandedOverrides, activeSubTabIndex]);
  return (
    <CardBaseTemplate breadcrumbItems={breadcrumbItems}>
      <Body>
        <H2>
          {displayTitle}{" "}
          {result.omschrijving ? `(${result.omschrijving})` : null}
        </H2>

        {versions && (
          <VersionSelector
            selectedVersionUUID={getZaaktypeUUID(result)}
            versions={versions}
            onVersionChange={handleVersionChange}
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
    </CardBaseTemplate>
  );
}

type ZaaktypeTabProps = {
  tabConfig: LeafTabConfig<TargetType>;
  result: TargetType;
  expandedOverrides: Partial<Record<keyof TargetType, ReactNode>>;
};
/** Renders a single tab */
const ZaaktypeTab = ({
  tabConfig,
  result,
  expandedOverrides,
}: ZaaktypeTabProps) => {
  if (tabConfig.view === "AttributeGrid") {
    return (
      <AttributeGrid
        object={{ ...result, ...expandedOverrides } as TargetType}
        fieldsets={tabConfig.fieldsets}
      />
    );
  }

  return expandedOverrides[tabConfig.key as keyof TargetType];
};

type RelatedObjectRendererProps = {
  relatedObjects: Record<ExpandItemKeys, Primitive | object>[];
  config: LeafTabConfig<TargetType>;
};

/**
 * Renders either a DataGrid or a list of badges for a set of related objects,
 * depending on the tab configuration.
 *
 * @param relatedObjects - The array of objects to render
 * @param config - Tab configuration indicating view type and allowed fields
 */
function RelatedObjectRenderer({
  relatedObjects,
  config,
}: RelatedObjectRendererProps) {
  if (config.view === "DataGrid") {
    return (
      <DataGrid
        objectList={relatedObjects}
        fields={config.allowedFields}
        urlFields={[]}
      />
    );
  }

  return (
    <>
      {relatedObjects.map((relatedObject, index) => (
        <RelatedObjectBadge
          key={
            typeof relatedObject.url === "string" ? relatedObject.url : index
          }
          relatedObject={relatedObject}
          allowedFields={config.allowedFields}
        />
      ))}
    </>
  );
}

type RelatedObjectBadgeProps = {
  relatedObject: Record<ExpandItemKeys, Primitive | object>;
  allowedFields: ExpandItemKeys[];
};

/**
 * Finds the first primitive field in `relatedObject` that is allowed,
 * then displays its value inside a Badge. Throws if no allowed key is found.
 *
 * @param relatedObject - Single related resource object
 * @param allowedFields - List of field names permitted for display
 * @returns A Badge containing the primitive value, or null for non-primitives
 * @throws InvalidRelatedObjectError When no allowed key exists
 */
function RelatedObjectBadge({
  relatedObject,
  allowedFields,
}: RelatedObjectBadgeProps) {
  const key = Object.keys(relatedObject).find((k): k is ExpandItemKeys =>
    allowedFields.includes(k as ExpandItemKeys),
  );
  // Bail early, no renderable data.
  if (!key) {
    throw new InvalidRelatedObjectError({
      object: relatedObject,
      allowedFields,
    });
  }

  // Extract value.
  const value = relatedObject[key];
  return isPrimitive(value) ? <Badge>{value}</Badge> : null;
}

export class InvalidRelatedObjectError extends Error {
  constructor(data: unknown) {
    const baseMessage =
      "<RelatedObjectList /> received an invalid related object";
    const detail =
      data && typeof data === "object"
        ? `: ${JSON.stringify(data, null, 2)}`
        : "";

    super(`${baseMessage}${detail}`);
    this.name = "InvalidRelatedObjectError";
  }
}

import {
  AttributeGrid,
  Badge,
  Body,
  Button,
  CardBaseTemplate,
  Column,
  DataGrid,
  Grid,
  H2,
  Primitive,
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
import { useBreadcrumbItems } from "~/hooks";
import { useHashParam } from "~/hooks/useHashParam.ts";
import { useSubmitAction } from "~/hooks/useSubmitAction.ts";
import { getZaaktypeUUID, isPrimitive } from "~/lib";
import {
  AttributeGridSection,
  DataGridSection,
  ExpandItemKeys,
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
          config={activeSectionConfig}
          view={TABS_CONFIG[activeTabIndex].view}
        />
      );
    }

    return overrides;
    // TODO: Optimize this by inspecting if the field is part of the active tab.
  }, [fields, result, activeTabIndex]);

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
                  tabConfig={activeSectionConfig}
                />
              </Column>
            </Grid>
          ) : (
            <ZaaktypeTab
              view={tabConfig.view}
              expandedOverrides={expandedOverrides}
              result={result}
              tabConfig={tabConfig.sections[0]}
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

function isAttributeGridSection(
  view: string,
  // @ts-expect-error - TypeScript unhappy with unused, but necessary for type guard
  tabConfig: AttributeGridSection<TargetType> | DataGridSection,
): tabConfig is AttributeGridSection<TargetType> {
  return view === "AttributeGrid";
}

type ZaaktypeTabProps = {
  tabConfig: AttributeGridSection<TargetType> | DataGridSection;
  view: "AttributeGrid" | "DataGrid";
  result: TargetType;
  expandedOverrides: Partial<Record<keyof TargetType, ReactNode>>;
};
/** Renders a single tab */
const ZaaktypeTab = ({
  tabConfig,
  view,
  result,
  expandedOverrides,
}: ZaaktypeTabProps) => {
  if (isAttributeGridSection(view, tabConfig)) {
    return (
      <AttributeGrid
        object={{ ...result, ...expandedOverrides } as TargetType}
        fieldsets={tabConfig.fieldsets}
      />
    );
  }

  return expandedOverrides[tabConfig.key];
};

type RelatedObjectRendererProps = {
  relatedObjects: Record<ExpandItemKeys, Primitive | object>[];
  view: "AttributeGrid" | "DataGrid";
  config: AttributeGridSection<TargetType> | DataGridSection;
};

/**
 * Renders either a DataGrid or a list of badges for a set of related objects,
 * depending on the tab configuration.
 *
 * @param relatedObjects - The array of objects to render
 * @param view - The view type, either "DataGrid" or "AttributeGrid"
 * @param config - Tab configuration indicating view type and allowed fields
 */
function RelatedObjectRenderer({
  relatedObjects,
  view,
  config,
}: RelatedObjectRendererProps) {
  if (!isAttributeGridSection(view, config)) {
    return (
      <DataGrid
        objectList={relatedObjects}
        fields={config.expandFields}
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
          allowedFields={config.expandFields}
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
  const objectKeys = Object.keys(
    relatedObject,
  ) as (keyof typeof relatedObject)[];

  const key = objectKeys.find((k) => allowedFields.includes(k));
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

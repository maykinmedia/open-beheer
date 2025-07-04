import {
  AttributeGrid,
  Badge,
  Body,
  CardBaseTemplate,
  DataGrid,
  H2,
  Primitive,
  Tab,
  Tabs,
} from "@maykin-ui/admin-ui";
import { ucFirst } from "@maykin-ui/client-common";
import { ReactNode, useCallback, useMemo, useState } from "react";
import { useLoaderData, useNavigate } from "react-router";
import { VersionSelector } from "~/components/VersionSelector";
import { useBreadcrumbItems } from "~/hooks";
import { getZaaktypeUUID, isPrimitive } from "~/lib";
import {
  ExpandItemKeys,
  TAB_CONFIG_OVERVIEW,
  TabConfig,
  TargetType,
  ZaaktypeLoaderData,
} from "~/pages";
import { TAB_CONFIG_STATUSTYPEN } from "~/pages/zaaktype/tabs/statustypen.ts";
import { components } from "~/types";

const TAB_CONFIGS: TabConfig<TargetType>[] = [
  TAB_CONFIG_OVERVIEW,
  TAB_CONFIG_STATUSTYPEN,
];

/**
 * Renders the detail view for a single zaaktype, with tabs for attributes and related data.
 */
export function ZaaktypePage() {
  const navigate = useNavigate();
  const breadcrumbItems = useBreadcrumbItems();
  const [activeTabIndex, setActiveTabIndex] = useState(0);

  const { fields, result, versions } = useLoaderData() as ZaaktypeLoaderData;

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
          config={TAB_CONFIGS[activeTabIndex]}
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
    return TAB_CONFIGS.map((tabConfig) => ({
      label: tabConfig.label,
      element: (
        <ZaaktypeTab
          tabConfig={tabConfig}
          result={result}
          expandedOverrides={expandedOverrides}
        />
      ),
    }));
  }, [result, expandedOverrides]);
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

        <Tabs activeTabIndex={activeTabIndex} onTabChange={setActiveTabIndex}>
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
  tabConfig: TabConfig<TargetType>;
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

  return (
    <DataGrid
      objectList={
        (result._expand?.[tabConfig.key] as
          | Record<ExpandItemKeys, object | Primitive>[]
          | undefined) ?? []
      }
      fields={tabConfig.allowedFields}
    />
  );
};

type RelatedObjectRendererProps = {
  relatedObjects: Record<ExpandItemKeys, Primitive | object>[];
  config: TabConfig<TargetType>;
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

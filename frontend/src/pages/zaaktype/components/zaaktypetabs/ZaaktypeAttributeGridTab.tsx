import {
  AttributeGrid,
  Column,
  Field,
  FieldSet,
  Grid,
  Sidebar,
  Toolbar,
  fields2TypedFields,
  isPrimitive,
} from "@maykin-ui/admin-ui";
import { invariant, slugify } from "@maykin-ui/client-common";
import React, { ReactNode, useCallback, useMemo } from "react";
import { useLoaderData, useLocation, useParams } from "react-router";
import {
  RelatedObjectBadge,
  RelatedObjectRenderer,
  getObjectValue,
} from "~/components/related";
import { useErrors } from "~/hooks";
import { useHashParam } from "~/hooks/useHashParam.ts";
import {
  AttributeGridTabConfig,
  TargetType,
  ZaaktypeLoaderData,
} from "~/pages";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { Expand, ExpandItemKeys, RelatedObject } from "~/types";

type ZaaktypeAttributeGridTabProps = {
  object: TargetType;
  tabConfig: AttributeGridTabConfig<TargetType>;
  onChange: React.ChangeEventHandler;
};

/**
 * Renders an AttributeGrid tab for a Zaaktype.
 * Supports multiple vertical sections and dynamically replaces
 * complex or expanded fields with related object renderers.
 */
export const ZaaktypeAttributeGridTab = ({
  object,
  tabConfig,
  onChange,
}: ZaaktypeAttributeGridTabProps) => {
  const { fields } = useLoaderData() as ZaaktypeLoaderData;
  const location = useLocation();
  const { serviceSlug } = useParams();
  invariant(serviceSlug, "serviceSlug must be provided!");

  const isEditing =
    new URLSearchParams(location.search).get("editing") === "true";

  // Extract errors
  const errors = useErrors<ZaaktypeAction>(
    (action) => action.type === "UPDATE_VERSION",
  );

  // (Vertical) section state
  const [sectionHash, setSectionHash] = useHashParam("section", "0");
  const activeSectionIndex = parseInt(sectionHash || "0");

  // Active section configuration
  const activeSectionConfig = useMemo(() => {
    return tabConfig.sections[activeSectionIndex] || tabConfig.sections[0];
  }, [tabConfig, activeSectionIndex]);

  // Check if tab has multiple vertical subtabs
  const doesActiveTabHaveMultipleSubTabs = useMemo(() => {
    return tabConfig.sections.length > 1;
  }, [tabConfig]);

  /**
   * Maps complex (non-primitive) fields to rendered components.
   * Non-primitive values are displayed as RelatedObjectBadge or editable text.
   */
  const complexOverrides = useMemo(() => {
    const overrides: Partial<Record<keyof TargetType, ReactNode>> = {};

    for (const field of fields) {
      const _fieldName = field.name.split(".").pop();
      if (!_fieldName || !(_fieldName in object)) continue;

      const fieldName = _fieldName as keyof TargetType;
      const originalValue = object[fieldName];

      if (
        originalValue &&
        !isPrimitive(originalValue) &&
        !Array.isArray(originalValue)
      ) {
        overrides[fieldName] = isEditing ? (
          getObjectValue(originalValue)
        ) : (
          <RelatedObjectBadge relatedObject={originalValue} />
        );
      }
    }
    return overrides;
  }, [fields, object]);

  /**
   * Maps expandable fields to rendered components showing related data.
   * Uses `RelatedObjectRenderer` to visualize expanded content.
   */
  const expandedOverrides = useMemo(() => {
    if (!object || !object._expand) return {};

    const overrides: Partial<Record<keyof TargetType, ReactNode>> = {};
    for (const field of fields) {
      const fieldName = field.name.split(".").pop() as keyof TargetType;
      const originalValue = object[fieldName];
      const expand = object._expand;
      const relatedObject = expand[fieldName as keyof Expand<TargetType>];

      if (!(fieldName in expand) || originalValue === null) continue;
      if (isEditing && field.options) continue;

      overrides[fieldName] = (
        <RelatedObjectRenderer
          expandFields={fields2TypedFields(
            (activeSectionConfig.expandFields || []) as Field[],
          )}
          object={object}
          relatedObject={relatedObject as RelatedObject<TargetType>}
          relatedObjectKey={fieldName as ExpandItemKeys<TargetType>}
          fields={fields2TypedFields(fields as Field[])}
        />
      );
    }
    return overrides;
  }, [object, fields, tabConfig, activeSectionConfig]);

  /**
   * Updates the active section when a user switches vertical tabs.
   */
  const handleSectionChange = useCallback(
    (index: number) => {
      setSectionHash(index.toString());
    },
    [setSectionHash],
  );

  /**
   * Builds the AttributeGrid for the active section.
   * Merges overrides for complex and expanded fields.
   */
  const contents = useMemo(() => {
    const fieldsets = activeSectionConfig.fieldsets.map((fieldset) => [
      fieldset[0],
      {
        ...fieldset[1],
        fields: fieldset[1].fields.map((fieldsetField) => {
          const field = fields.find((field) => field.name === fieldsetField);

          const nameBits = field ? field.name.split(".") : [];
          if (nameBits.length > 1) {
            // For some reason, adding a valueLookup = field.name doesn't work.
            let objectValue = object;
            for (const nameBit of nameBits) {
              if (nameBit in objectValue) {
                // @ts-expect-error - # TODO: I don't know how to type this :(
                objectValue = objectValue[nameBit];
              } else {
                break;
              }
            }
            // @ts-expect-error - # TODO: I don't know how to type this :(
            object[field.name] = objectValue;
          }

          const editable =
            field?.name && field.name in expandedOverrides
              ? false
              : field?.editable;
          return { ...field, editable };
        }),
      },
    ]) as FieldSet<TargetType>[];

    return (
      <AttributeGrid
        object={
          {
            ...object,
            ...complexOverrides,
            ...expandedOverrides,
          } as TargetType
        }
        decorate
        editable={isEditing ? undefined : false}
        editing={isEditing}
        errors={errors}
        fieldsets={fieldsets}
        formControlProps={{
          pad: true,
        }}
        onChange={onChange}
      />
    );
  }, [
    activeSectionConfig,
    fields,
    object,
    complexOverrides,
    expandedOverrides,
    isEditing,
    onChange,
  ]);

  // Render with or without vertical sidebar
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
              onClick: () => handleSectionChange(index),
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

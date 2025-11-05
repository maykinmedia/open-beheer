import {
  AttributeGrid,
  Badge,
  Column,
  Field,
  FieldSet,
  Grid,
  Option,
  Sidebar,
  Toolbar,
  TypedField,
  fields2TypedFields,
  isPrimitive,
} from "@maykin-ui/admin-ui";
import { invariant, slugify } from "@maykin-ui/client-common";
import React, {
  ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useLoaderData, useLocation, useParams } from "react-router";
import { getZaaktype, getZaaktypen } from "~/api/zaaktype.ts";
import {
  RelatedObjectBadge,
  RelatedObjectRenderer,
  getObjectValue,
} from "~/components/related";
import { Errors } from "~/hooks";
import { useHashParam } from "~/hooks/useHashParam.ts";
import { getZaaktypeUUID } from "~/lib";
import {
  AttributeGridTabConfig,
  TargetType,
  ZaaktypeLoaderData,
} from "~/pages";
import { Expand, ExpandItemKeys, RelatedObject, components } from "~/types";

type ZaaktypeAttributeGridTabProps = {
  errors: Errors<TargetType>;
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
  errors,
  object,
  tabConfig,
  onChange,
}: ZaaktypeAttributeGridTabProps) => {
  const { fields } = useLoaderData() as ZaaktypeLoaderData;
  const location = useLocation();
  const { serviceSlug, catalogusId } = useParams();
  invariant(serviceSlug, "serviceSlug must be provided!");

  const isEditing =
    new URLSearchParams(location.search).get("editing") === "true";

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

  const [selectedDeelzaaktypenOptions, setSelectedDeelzaaktypenOptions] =
    useState<Option[]>([]);

  const mapZaaktypenToOptions = (
    zaaktypen:
      | components["schemas"]["ExpandableZaakType"]
      | components["schemas"]["ExpandableZaakType"][],
  ): Option[] => {
    const list = Array.isArray(zaaktypen) ? zaaktypen : [zaaktypen];

    return list.map((z) => ({
      label: `${z.identificatie} - ${z.omschrijving}`,
      value: z.url,
    }));
  };

  /**
   * Fetches and sets selected deelzaaktypen options when not editing.
   */
  useEffect(() => {
    if (isEditing) return;

    const deelzaaktypenField = fields.find(
      (f) => f.name.split(".").pop() === "deelzaaktypen",
    );
    if (!deelzaaktypenField) return;

    const raw = object["deelzaaktypen" as keyof TargetType];

    if (!Array.isArray(raw)) return;

    const run = async () => {
      const urls = raw as string[];

      const fetches = urls.map((url) => {
        const zaaktypeUUID = getZaaktypeUUID({ url });
        return zaaktypeUUID ? getZaaktype({ serviceSlug, zaaktypeUUID }) : null;
      });

      const results = await Promise.all(fetches);
      const zaaktypen = results
        .filter((res) => res !== null)
        .map((res) => res.result);

      setSelectedDeelzaaktypenOptions(mapZaaktypenToOptions(zaaktypen));
    };

    void run();
  }, [isEditing, fields, object, serviceSlug]);

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

      if (!originalValue || isPrimitive(originalValue)) continue;

      // When deelzaaktypen we want to render badges for selected options
      if (fieldName === "deelzaaktypen") {
        overrides[fieldName] = isEditing
          ? (originalValue as string[])
          : selectedDeelzaaktypenOptions.length > 0
            ? selectedDeelzaaktypenOptions.map((option) => (
                <Badge
                  key={option.value}
                  href={
                    option.value
                      ? `/${serviceSlug}/${catalogusId}/zaaktypen/${getZaaktypeUUID({ url: String(option.value) })}`
                      : undefined
                  }
                >
                  {option.label}
                </Badge>
              ))
            : "-";
        continue;
      }

      if (!Array.isArray(originalValue)) {
        overrides[fieldName] = isEditing ? (
          getObjectValue(originalValue)
        ) : (
          <RelatedObjectBadge relatedObject={originalValue} />
        );
      }
    }
    return overrides;
  }, [fields, object, selectedDeelzaaktypenOptions]);

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

  const fetchDeelzaaktypen = async (query: string) => {
    const _query = query.trim().toLowerCase();
    if (_query.length <= 2) return [];

    if (!serviceSlug || !catalogusId) {
      throw new Error("serviceSlug and catalogusId must be provided!"); // Shouldn't happen
    }
    const [byIdent, byOmschrijving] = await Promise.all([
      getZaaktypen({
        serviceSlug,
        catalogusId,
        identificatie: _query,
      }),
      getZaaktypen({
        serviceSlug,
        catalogusId,
        omschrijving: _query,
      }),
    ]);

    const allResults = [...byIdent.results, ...byOmschrijving.results];
    const unique = Array.from(
      new Map(allResults.map((zaaktype) => [zaaktype.url, zaaktype])).values(),
    );

    return unique.map((zaaktype) => ({
      label: `${zaaktype.identificatie} - ${zaaktype.omschrijving}`,
      value: zaaktype.url,
    }));
  };

  const fieldPatches = useMemo<Record<string, Partial<TypedField>>>(
    () => ({
      deelzaaktypen: {
        options: fetchDeelzaaktypen,
        multiple: true,
        placeholder: "Kies één of meer deelzaaktypen",
        fetchOnMount: true,
      },
    }),
    [],
  );

  const getFieldPatch = (
    fieldName?: string,
  ): Partial<TypedField> | undefined =>
    fieldName ? fieldPatches[fieldName] : undefined;

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
          const editable =
            field?.name && field.name in expandedOverrides
              ? false
              : field?.editable;
          const patch = getFieldPatch(field?.name);
          return {
            ...field,
            editable,
            ...patch,
          };
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

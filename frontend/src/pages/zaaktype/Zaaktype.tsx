import {
  AttributeGrid,
  Body,
  CardBaseTemplate,
  Column,
  Field,
  FieldSet,
  Grid,
  H2,
  Outline,
  Sidebar,
  Solid,
  Tab,
  Tabs,
  Toolbar,
  TypedField,
  fields2TypedFields,
  isPrimitive,
  useFormDialog,
} from "@maykin-ui/admin-ui";
import { slugify, ucFirst } from "@maykin-ui/client-common";
import { invariant } from "@maykin-ui/client-common/assert";
import React, {
  ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useLoaderData, useParams } from "react-router";
import { VersionSelector } from "~/components/VersionSelector";
import {
  RelatedObjectBadge,
  RelatedObjectDataGrid,
  RelatedObjectRenderer,
  getObjectKey,
  getObjectValue,
} from "~/components/related";
import zaaktype from "~/fixtures/zaaktype.ts";
import {
  useBreadcrumbItems,
  useCombinedSearchParams,
  useErrors,
} from "~/hooks";
import { useHashParam } from "~/hooks/useHashParam.ts";
import { TypedAction, useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import { findConceptZaaktypeVersion, getZaaktypeUUID } from "~/lib";
import {
  findActiveZaaktypeVersion,
  sortZaaktypeVersions,
} from "~/lib/zaaktype";
import { getZaaktypeCreateFields } from "~/lib/zaaktype/zaaktypeCreate.ts";
import {
  AttributeGridSection,
  AttributeGridTabConfig,
  DataGridSection,
  DataGridTabConfig,
  TAB_CONFIG_ALGEMEEN,
  TAB_CONFIG_OVERVIEW,
  TabConfig,
  TargetType,
  ZaaktypeLoaderData,
} from "~/pages";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { Expand, ExpandItemKeys, RelatedObject } from "~/types";

/** Explicit tab configs specified ./tabs, overrides tab config resolved from fieldset. */
const TAB_CONFIG_OVERRIDES: TabConfig<TargetType>[] = [
  TAB_CONFIG_OVERVIEW,
  TAB_CONFIG_ALGEMEEN,
];

/**
 * Renders the detail view for a single zaaktype, with tabs for attributes and related data.
 */
export function ZaaktypePage() {
  const { fields, fieldsets, result, versions } =
    useLoaderData() as ZaaktypeLoaderData;

  const [pendingUpdatesState, setPendingUpdatesState] =
    useState<Partial<TargetType> | null>(null);
  const possiblyUpdatedResult = { ...result, ...pendingUpdatesState };

  // Related objects (array) changes are recorded as actions instead of mutations
  // directly to the object.
  const [actionsState, setActionsState] = useState<
    Record<TabConfig<TargetType>["key"], ZaaktypeAction[]>
  >({});
  useEffect(() => {
    setActionsState({});
  }, [result]);

  const formDialog = useFormDialog();

  const breadcrumbItems = useBreadcrumbItems();
  const submitAction = useSubmitAction<ZaaktypeAction>();

  const { serviceSlug } = useParams();
  invariant(serviceSlug, "serviceSlug must be provided!");

  // Versions sorted by date.
  const sortedVersions = useMemo(
    () => sortZaaktypeVersions(versions || []),
    [versions],
  );

  // The (last) concept version, we assume there should be max 1.
  const conceptVersion = useMemo(
    () => findConceptZaaktypeVersion(sortedVersions),
    [sortedVersions],
  );

  // The current active (but not necessarily selected) versions
  const currentVersion = useMemo(
    () => findActiveZaaktypeVersion(versions || []),
    [sortedVersions],
  );

  // Convert FieldSet[] to TabConfig[].
  const fieldSetTabConfigs = useMemo<TabConfig<TargetType>[]>(
    () =>
      fieldsets
        .map((fieldset) => {
          const [label, { fields }] = fieldset;
          const key = slugify(label);

          // _expand fields imply DataGrid.
          const fieldsAreExpanded = fields.find((field) =>
            field.includes("_expand"),
          );
          const view = fieldsAreExpanded ? "DataGrid" : "AttributeGrid";

          if (view === "AttributeGrid") {
            return {
              key: slugify(label),
              label,
              view,
              sections: [{ label, fieldsets: [[label, { fields }]] }],
            } as AttributeGridTabConfig<TargetType>;
          }

          return {
            key: key,
            fieldset: fieldset as unknown as FieldSet,
            label,
            view,
            sections: [{ label, key: slugify(label) }],
          } as DataGridTabConfig<TargetType>;
        })
        .filter((tabConfig): tabConfig is TabConfig<TargetType> =>
          Boolean(tabConfig),
        ),
    [JSON.stringify([fields, fieldsets])],
  );

  // Allow custom TabConfig's to override `fieldSetTabConfigs` (matches by `key`).
  const tabConfigs = useMemo<TabConfig<TargetType>[]>(
    () =>
      fieldSetTabConfigs.map((fieldSetTabConfig) => {
        const override = TAB_CONFIG_OVERRIDES.find(
          (tabConfig) => tabConfig.key === fieldSetTabConfig.key,
        );
        return override ?? fieldSetTabConfig;
      }),
    // .filter((_, i) => i === 5),
    [],
  );

  /**
   * Gets called when the edit button is clicked.
   */
  const handleVersionCreate = useCallback<React.MouseEventHandler>(() => {
    submitAction({
      type: "CREATE_VERSION",
      payload: { serviceSlug: serviceSlug as string, zaaktype: result },
    });
  }, [serviceSlug, result]);

  /**
   * Gets called when the edit button is clicked.
   */
  const handleEdit = useCallback<React.MouseEventHandler>(() => {
    invariant(conceptVersion, "concept version (uuid) must be set");

    submitAction({
      type: "EDIT_VERSION",
      payload: {
        uuid: conceptVersion.uuid,
      },
    });
  }, [conceptVersion?.uuid]);

  /**
   * Gets called when the cancel button is clicked.
   */
  const handleCancel = useCallback<React.MouseEventHandler>(() => {
    invariant(conceptVersion, "concept version (uuid) must be set");
    setPendingUpdatesState(null);
    setActionsState({});

    submitAction({
      type: "EDIT_CANCEL",
      payload: {
        uuid: currentVersion?.uuid || conceptVersion.uuid,
      },
    });
  }, [currentVersion?.uuid, conceptVersion?.uuid]);

  /**
   * Gets called when the relatedObject is changed.
   */
  const handleChange: React.ChangeEventHandler<
    HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
  > = useCallback(
    (e) => {
      const key = e.target.name as keyof TargetType;
      const originalValue = result[key];

      // Whether originalValue is an object.
      const isObject =
        originalValue &&
        typeof originalValue === "object" &&
        !Array.isArray(result[key]);

      // The new value.
      const value =
        e.target instanceof HTMLInputElement &&
        Object.hasOwn(e.target, "checked")
          ? e.target.checked
          : e.target.value;

      // When rendering an object, it's value is converted to string using an
      // override (see `ZaaktypeTab`. When changing its value (and creating a
      // pending update), the original shape needs to be restored.
      //
      // @see `ZaaktypeTab.complexOverrides`
      if (isObject) {
        const objectKey = getObjectKey(originalValue) as string;
        const objectValue = { ...originalValue, [objectKey]: value };

        // Update pending changes, but restore object shape.
        setPendingUpdatesState({
          ...pendingUpdatesState,
          [key]: objectValue,
          url: result.url, // Required for API communication.
        });

        return;
      }

      // Update pending changes.
      setPendingUpdatesState({
        ...pendingUpdatesState,
        [key]: value,
        url: result.url, // Required for API communication.
      });
    },
    [pendingUpdatesState, result],
  );

  /**
   * Gets called with a `TabConfig` and a list of `ZaaktypeAction`s to perform
   * when mutations are made in a `<RelatedObjectDataGrid>`, these actions need
   * to submitted to the backend in order to be persisted.
   */
  const handleTabActionsChange = useCallback(
    (tabConfig: TabConfig<TargetType>, actions: ZaaktypeAction[]) => {
      const newActionsState = { ...actionsState, [tabConfig.key]: actions };
      setActionsState(newActionsState);
    },
    [tabConfigs, actionsState, setActionsState],
  );

  /**
   * Gets called when the edit button is clicked.
   */
  const handleSave = useCallback<React.MouseEventHandler>(async () => {
    invariant(conceptVersion, "concept version (uuid) must be set");
    const zaaktype = result;

    const deletions: ZaaktypeAction[] = [];
    const updates: ZaaktypeAction[] = [];

    const actions = Object.values(actionsState).flat().filter(Boolean);
    actions.forEach((action) => {
      const isDeletion = action.type.toUpperCase().includes("DELETE");
      if (isDeletion) {
        deletions.push(action);
      } else {
        updates.push(action);
      }
    });

    // First run deletions.
    await submitAction({
      type: "BATCH",
      payload: {
        zaaktype: { ...(pendingUpdatesState || {}), uuid: conceptVersion.uuid },
        actions: deletions,
      },
    });

    // Run updates after deletions are complete.
    await submitAction({
      type: "BATCH",
      payload: {
        zaaktype,
        actions: [
          {
            type: "UPDATE_VERSION",
            payload: {
              serviceSlug: serviceSlug as string,
              zaaktype: {
                ...(pendingUpdatesState || {}),
                uuid: conceptVersion?.uuid,
              },
            },
          },
          ...updates, // FIXME: Investigate why no work
        ],
      },
    });

    // Reset pending changes.
    setPendingUpdatesState(null);
    setActionsState({});
  }, [
    result,
    actionsState,
    pendingUpdatesState,
    conceptVersion?.uuid,
    serviceSlug,
  ]);

  /**
   * Gets called when the edit button is clicked.
   */
  const handleSaveAs = useCallback<React.MouseEventHandler>(async () => {
    const fields = getZaaktypeCreateFields();

    const handle = (overrides: Partial<TargetType>) => {
      const zaaktype = { ...result, ...overrides };

      submitAction({
        type: "SAVE_AS",
        payload: {
          serviceSlug: serviceSlug as string,
          zaaktype,
        },
      });
    };

    formDialog(
      "Opslaan als nieuw Zaaktype",
      "",
      fields,
      "Zaaktype aanmaken",
      "Annuleren",
      handle,
    );
  }, [result, serviceSlug, zaaktype, fields, pendingUpdatesState]);

  /**
   * Gets called when the edit button is clicked.
   */
  const handlePublish = useCallback<React.MouseEventHandler>(() => {
    invariant(conceptVersion, "concept version (uuid) must be set");

    submitAction({
      type: "PUBLISH_VERSION",
      payload: {
        serviceSlug: serviceSlug as string,
        zaaktype: { ...(pendingUpdatesState || {}), uuid: conceptVersion.uuid },
        versions: sortedVersions,
      },
    });
  }, [serviceSlug, pendingUpdatesState, conceptVersion?.uuid, sortedVersions]);

  return (
    <CardBaseTemplate
      breadcrumbItems={breadcrumbItems}
      cardProps={{
        justify: "space-between",
      }}
    >
      <Body fullHeight>
        <H2>
          {ucFirst(possiblyUpdatedResult.identificatie ?? "")}{" "}
          {result.omschrijving
            ? `(${possiblyUpdatedResult.omschrijving})`
            : null}
        </H2>

        {versions && (
          <VersionSelector
            selectedVersionUUID={getZaaktypeUUID(result)!}
            versions={versions}
            onVersionChange={({ uuid }) =>
              submitAction({
                type: "SELECT_VERSION",
                payload: { uuid },
              })
            }
          />
        )}
        <ZaaktypeTabs
          object={possiblyUpdatedResult}
          tabConfigs={tabConfigs}
          onChange={handleChange}
          onTabActionsChange={handleTabActionsChange}
        />
      </Body>

      <ZaaktypeToolbar
        onCancel={handleCancel}
        onEdit={handleEdit}
        onPublish={handlePublish}
        onSave={handleSave}
        onSaveAs={handleSaveAs}
        onVersionCreate={handleVersionCreate}
      />
    </CardBaseTemplate>
  );
}

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
function ZaaktypeTabs({
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
      tabConfigs.map((tabConfig) => (
        <Tab key={tabConfig.label} label={tabConfig.label}>
          <ZaaktypeTab
            object={object}
            tabConfig={tabConfig}
            onChange={onChange}
            onTabActionsChange={onTabActionsChange}
          />
        </Tab>
      )),
    [tabConfigs, object, onChange],
  );

  return (
    <Tabs activeTabIndex={activeTabIndex} onTabChange={handleTabChange}>
      {tabs}
    </Tabs>
  );
}

type ZaaktypeTabProps = {
  object: TargetType;
  tabConfig: TabConfig<TargetType>;
  onChange: React.ChangeEventHandler;
  onTabActionsChange: (
    tabConfig: TabConfig<TargetType>,
    actions: ZaaktypeAction[],
  ) => void;
};

/**
 * Renders a single tab, optionally containing different (vertical) section.
 */
const ZaaktypeTab = ({
  object,
  tabConfig,
  onChange,
  onTabActionsChange,
}: ZaaktypeTabProps) => {
  const { fields } = useLoaderData() as ZaaktypeLoaderData;
  const [combinedSearchParams] = useCombinedSearchParams();
  const isEditing = Boolean(combinedSearchParams.get("editing"));
  const errors = useErrors();

  // (Vertical) section data.
  const [sectionHash, setSectionHash] = useHashParam("section", "0");
  const activeSectionIndex = parseInt(sectionHash || "0");

  // The active (vertical) section.
  const activeSectionConfig = useMemo(() => {
    return tabConfig.sections[activeSectionIndex] || tabConfig.sections[0];
  }, [tabConfig, activeSectionIndex]);

  // Whether (vertical) sections exist within the tab.
  const doesActiveTabHaveMultipleSubTabs = useMemo(() => {
    return tabConfig.sections.length > 1;
  }, [tabConfig]);

  /**
   * Memoizes a version of the result relatedObject where complex fields
   * are replaced by React nodes rendering their data.
   *
   * @see `ZaaktypePage.handleChange`: this converts an object to string for
   *  presentation/editing. This operation is inverted by the change handler.
   * @returns A shallow copy of `result` with expanded fields replaced
   */
  const complexOverrides = useMemo(() => {
    const overrides: Partial<Record<keyof TargetType, ReactNode>> = {};

    for (const field of fields) {
      const fieldName = field.name.split(".").pop() as keyof TargetType;
      const originalValue = object[fieldName];

      // Show object values.
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
   * FIXME: Only used for AttributeGrid, refactor.
   *
   * Memoizes a version of the result relatedObject where expandable fields
   * are replaced by React nodes rendering related data.
   *
   * @returns A shallow copy of `result` with expanded fields replaced
   */
  const expandedOverrides = useMemo(() => {
    if (!object || !object._expand) return {};

    const overrides: Partial<Record<keyof TargetType, ReactNode>> = {};

    for (const field of fields) {
      const fieldName = field.name.split(".").pop() as keyof TargetType;
      const originalValue = object[fieldName];
      const expand = object._expand;

      // Skip if the field is not expandable or has no value.
      if (!(fieldName in expand) || originalValue === null) {
        continue;
      }
      const expandKey = fieldName as keyof Expand<TargetType>;
      const expandValue = expand[expandKey]!;

      const transform = activeSectionConfig?.valueTransform;
      const transformFn = transform?.[expandKey];
      const relatedObject = transformFn
        ? // @ts-expect-error - TS can't infer expandValue correctly here.
          transformFn(expandValue)
        : expandValue;

      // Related fields that are directly editable should not be in overrides.
      if (isEditing && field.options) {
        continue;
      }

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
   * Gets called when the (vertical) section is changed.
   */
  const handleSectionChange = useCallback(
    (index: number) => {
      setSectionHash(index.toString());
    },
    [setSectionHash],
  );

  /**
   * Gets called with a list of actions to perform when mutations are made in
   * a `<RelatedObjectDataGrid>`, these actions need to submitted to the backend
   * in order to be persisted.
   */
  const handleActionsChange = useCallback(
    (actions: TypedAction<string, object>[]) => {
      onTabActionsChange(tabConfig, actions as ZaaktypeAction[]);
    },
    [tabConfig, onTabActionsChange],
  );

  /**
   * The <AttributeGrid/> with the data for the current tab/section.
   */
  const contents = useMemo(() => {
    if (tabConfig.view === "DataGrid") {
      const key = tabConfig.key;
      const relatedObjects = object._expand[key] || [];
      invariant(
        Array.isArray(relatedObjects),
        "relatedObjects must be an Array for RelatedObjectDataGrid!",
      );

      return (
        <RelatedObjectDataGrid
          object={object}
          relatedObjects={relatedObjects}
          relatedObjectKey={tabConfig.key}
          fields={fields as TypedField[]}
          fieldset={tabConfig.fieldset}
          onActionsChange={handleActionsChange}
        />
      );
    }

    if (isAttributeGridSection(tabConfig.view, activeSectionConfig)) {
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
          editable={isEditing ? undefined : false} // When in edit mode, allow fields to defined editable state, prevent editing otherwise.
          editing={isEditing}
          errors={errors}
          fieldsets={fieldsets}
          onChange={onChange}
        />
      );
    }

    return expandedOverrides[activeSectionConfig.key];
  }, [
    tabConfig.view,
    activeSectionConfig,
    object,
    expandedOverrides,
    onChange,
  ]);

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

type ZaaktypeToolbarProps = {
  onCancel: React.MouseEventHandler;
  onEdit: React.MouseEventHandler;
  onPublish: React.MouseEventHandler;
  onSave: React.MouseEventHandler;
  onSaveAs: React.MouseEventHandler;
  onVersionCreate: React.MouseEventHandler;
};

/**
 * Renders the bottom toolbar containing (primary) actions.
 */
function ZaaktypeToolbar({
  onCancel,
  onEdit,
  onPublish,
  onSave,
  onSaveAs,
  onVersionCreate,
}: ZaaktypeToolbarProps) {
  const { result, versions } = useLoaderData() as ZaaktypeLoaderData;
  const [combinedSearchParams] = useCombinedSearchParams();

  const button = useMemo(() => {
    if (versions?.some((v) => v.concept)) {
      if (!combinedSearchParams.get("editing")) {
        return [
          {
            children: (
              <>
                <Solid.PencilSquareIcon />
                Bewerken
              </>
            ),
            variant: "primary",
            onClick: onEdit,
          },
        ];
      } else {
        return [
          {
            children: (
              <>
                <Outline.NoSymbolIcon />
                Annuleren
              </>
            ),
            variant: "transparent",
            onClick: onCancel,
          },
          "spacer",
          {
            children: (
              <>
                <Outline.DocumentDuplicateIcon />
                Opslaan als nieuw Zaaktype
              </>
            ),
            variant: "transparent",
            onClick: onSaveAs,
          },
          {
            children: (
              <>
                <Outline.ArrowDownTrayIcon />
                Opslaan en afsluiten
              </>
            ),
            variant: "transparent",
            onClick: onSave,
          },
          {
            children: (
              <>
                <Outline.CloudArrowUpIcon />
                Publiceren
              </>
            ),
            variant: "primary",
            onClick: onPublish,
          },
        ];
      }
    } else {
      return [
        {
          children: (
            <>
              <Outline.PlusIcon />
              Nieuwe Versie
            </>
          ),
          variant: "primary",
          onClick: onVersionCreate,
        },
      ];
    }
  }, [result, combinedSearchParams, onEdit, onSave, onVersionCreate]);

  return (
    <Toolbar
      align="end"
      pad
      variant="transparent"
      sticky={"bottom"}
      items={button}
    ></Toolbar>
  );
}

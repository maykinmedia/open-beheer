import {
  AttributeGrid,
  Body,
  CardBaseTemplate,
  Column,
  FieldSet,
  Grid,
  H2,
  Outline,
  Sidebar,
  Solid,
  Tab,
  Tabs,
  Toolbar,
  fields2TypedFields,
  useFormDialog,
} from "@maykin-ui/admin-ui";
import { slugify, ucFirst } from "@maykin-ui/client-common";
import { invariant } from "@maykin-ui/client-common/assert";
import React, {
  ReactNode,
  Ref,
  useCallback,
  useMemo,
  useRef,
  useState,
} from "react";
import { useLoaderData, useParams } from "react-router";
import { VersionSelector } from "~/components/VersionSelector";
import {
  RelatedObjectRenderer,
  RelatedObjectRendererHandle,
} from "~/components/related";
import {
  useBreadcrumbItems,
  useCombinedSearchParams,
  useErrors,
} from "~/hooks";
import { useHashParam } from "~/hooks/useHashParam.ts";
import { useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import { getZaaktypeUUID } from "~/lib";
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
  const relatedRendererRef = useRef<RelatedObjectRendererHandle>(null);

  const { fields, fieldsets, result, versions } =
    useLoaderData() as ZaaktypeLoaderData;

  const [pendingUpdatesState, setPendingUpdatesState] = useState<
    Partial<TargetType> & { url: string }
  >({ url: result.url });
  const possiblyUpdatedResult = { ...result, ...pendingUpdatesState };

  const formDialog = useFormDialog();

  const breadcrumbItems = useBreadcrumbItems();
  const submitAction = useSubmitAction<ZaaktypeAction>();

  const { serviceSlug } = useParams();
  invariant(serviceSlug, "serviceSlug must be provided!");

  // Versions sorted by date.
  const sortedVersions = useMemo(
    () =>
      [...(versions || [])].sort(
        (a, b) =>
          new Date(a.beginGeldigheid).getTime() -
          new Date(b.beginGeldigheid).getTime(),
      ),
    [versions],
  );

  // The (last) concept version, we assume there should be max 1.
  const conceptVersion = useMemo(() => {
    const concepts = sortedVersions.filter((v) => v.concept);
    return concepts[0];
  }, [sortedVersions]);

  // The current active (but not necessarily selected) versions
  const today = new Date();
  const currentVersion = useMemo(
    () =>
      sortedVersions.find((v) => {
        const beginDate = new Date(v.beginGeldigheid);
        const endDate = v.eindeGeldigheid ? new Date(v.eindeGeldigheid) : null;

        return (
          !v.concept && beginDate <= today && (!endDate || endDate > today)
        );
      }),
    [sortedVersions],
  );

  // Convert FieldSet[] to TabConfig[].
  const fieldSetTabConfigs = useMemo<TabConfig<TargetType>[]>(
    () =>
      fieldsets.map((fieldset) => {
        const [label, { fields }] = fieldset;
        const expandFields = fields2TypedFields(
          fields.filter((field) => field.includes("_expand")),
        );
        const view = expandFields.length ? "DataGrid" : "AttributeGrid";

        if (view === "AttributeGrid") {
          return {
            key: slugify(label),
            label,
            view,
            sections: [
              { expandFields, label, fieldsets: [[label, { fields }]] },
            ],
          } as AttributeGridTabConfig<TargetType>;
        }

        return {
          key: slugify(label),
          label,
          view,
          sections: [{ expandFields, label, key: slugify(label) }],
        } as DataGridTabConfig<TargetType>;
      }),
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
    relatedRendererRef.current?.cancel();

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
      const key = e.target.name;
      const value =
        e.target instanceof HTMLInputElement &&
        Object.hasOwn(e.target, "checked")
          ? e.target.checked
          : e.target.value;

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
   * Gets called when the edit button is clicked.
   */
  const handleSave = useCallback<React.MouseEventHandler>(async () => {
    const saveActions = relatedRendererRef.current?.getSaveActions() || [];

    const zaaktype = result;

    const deletions: ZaaktypeAction[] = [];
    const updates: ZaaktypeAction[] = [];

    saveActions.forEach((action) => {
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
        zaaktype,
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
              zaaktype: pendingUpdatesState,
            },
          },
          ...updates,
        ],
      },
    });
  }, [serviceSlug, pendingUpdatesState]);

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
  }, [serviceSlug, pendingUpdatesState]);

  /**
   * Gets called when the edit button is clicked.
   */
  const handlePublish = useCallback<React.MouseEventHandler>(() => {
    submitAction({
      type: "PUBLISH_VERSION",
      payload: {
        serviceSlug: serviceSlug as string,
        zaaktype: pendingUpdatesState,
      },
    });
  }, [serviceSlug, pendingUpdatesState]);

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
          relatedRendererRef={relatedRendererRef}
          tabConfigs={tabConfigs}
          onChange={handleChange}
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
  relatedRendererRef: Ref<RelatedObjectRendererHandle>;
  tabConfigs: TabConfig<TargetType>[];
  onChange: React.ChangeEventHandler;
};

/**
 * Renders the tabs for a zaaktype
 */
function ZaaktypeTabs({
  object,
  relatedRendererRef,
  tabConfigs,
  onChange,
}: ZaaktypeTabsProps) {
  // (Horizontal) tab data.
  const [tabHash, setTabHash] = useHashParam("tab", "0");
  const activeTabIndex = parseInt(tabHash);

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
            relatedRendererRef={relatedRendererRef}
            tabConfig={tabConfig}
            onChange={onChange}
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
  relatedRendererRef: Ref<RelatedObjectRendererHandle>;
  tabConfig: TabConfig<TargetType>;
  onChange: React.ChangeEventHandler;
};

/**
 * Renders a single tab, optionally containing different (vertical) section.
 */
const ZaaktypeTab = ({
  object,
  relatedRendererRef,
  tabConfig,
  onChange,
}: ZaaktypeTabProps) => {
  const { fields } = useLoaderData() as ZaaktypeLoaderData;
  const [combinedSearchParams] = useCombinedSearchParams();
  const isEditing = Boolean(combinedSearchParams.get("editing"));
  const errors = useErrors();

  // (Vertical) section data.
  const [sectionHash, setSectionHash] = useHashParam("section", "0");
  const activeSectionIndex = parseInt(sectionHash);

  // The active (vertical) section.
  const activeSectionConfig = useMemo(() => {
    return tabConfig.sections[activeSectionIndex] || tabConfig.sections[0];
  }, [tabConfig, activeSectionIndex]);

  // Whether (vertical) sections exist within the tab.
  const doesActiveTabHaveMultipleSubTabs = useMemo(() => {
    return tabConfig.sections.length > 1;
  }, [tabConfig]);

  /**
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

      const zaaktypeUuid = getZaaktypeUUID(object);
      if (!zaaktypeUuid) {
        console.warn(
          "Zaaktype UUID is undefined, cannot render related object.",
        );
        continue;
      }

      // Related fields that are directly editable should not be in overrides.
      if (isEditing && field.options) {
        continue;
      }

      overrides[fieldName] = (
        // TODO: Handle errors for related objects.
        <RelatedObjectRenderer
          ref={relatedRendererRef}
          expandFields={activeSectionConfig.expandFields}
          object={object}
          relatedObject={relatedObject as RelatedObject<TargetType>}
          view={tabConfig.view}
          field={fieldName as ExpandItemKeys<TargetType>}
          fields={fields}
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
   * The <AttributeGrid/> with the data for the current tab/section.
   */
  const contents = useMemo(() => {
    if (isAttributeGridSection(tabConfig.view, activeSectionConfig)) {
      const fieldsets = activeSectionConfig.fieldsets.map((fs) => [
        fs[0],
        {
          ...fs[1],
          fields: fs[1].fields.map((f) => fields.find((lf) => lf.name === f)),
        },
      ]) as FieldSet<TargetType>[];

      return (
        <AttributeGrid
          object={{ ...object, ...expandedOverrides } as TargetType}
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

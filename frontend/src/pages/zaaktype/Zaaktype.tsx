import { Body, CardBaseTemplate, H2, useFormDialog } from "@maykin-ui/admin-ui";
import { ucFirst } from "@maykin-ui/client-common";
import { invariant } from "@maykin-ui/client-common/assert";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useLoaderData, useParams } from "react-router";
import { VersionSelector } from "~/components/VersionSelector";
import { getObjectKey } from "~/components/related";
import zaaktype from "~/fixtures/zaaktype.ts";
import { useBreadcrumbItems } from "~/hooks";
import { useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import {
  convertFieldsetsToTabConfig,
  findConceptZaaktypeVersion,
  getZaaktypeUUID,
} from "~/lib";
import {
  findActiveZaaktypeVersion,
  sortZaaktypeVersions,
} from "~/lib/zaaktype";
import { getZaaktypeCreateFields } from "~/lib/zaaktype/zaaktypeCreate.ts";
import {
  TAB_CONFIG_ALGEMEEN,
  TAB_CONFIG_OVERVIEW,
  TabConfig,
  TargetType,
  ZaaktypeLoaderData,
} from "~/pages";
import { ZaaktypeTabs, ZaaktypeToolbar } from "~/pages/zaaktype/components";
import {
  ZaaktypeAction,
  performAction,
} from "~/pages/zaaktype/zaaktype.action.ts";

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

  const isEditing =
    new URLSearchParams(location.search).get("editing") === "true";

  const [pendingUpdatesState, setPendingUpdatesState] =
    useState<Partial<TargetType> | null>(null);
  const possiblyUpdatedResult = { ...result, ...pendingUpdatesState };

  // Related objects (array) changes are recorded as actions instead of mutations
  // directly to the object.
  const [actionsState, setActionsState] = useState<
    Record<TabConfig<TargetType>["key"], ZaaktypeAction[]>
  >({});
  useEffect(() => {
    if (!isEditing) {
      setPendingUpdatesState(null);
      setActionsState({});
    }
  }, [isEditing]);

  const formDialog = useFormDialog();

  const breadcrumbItems = useBreadcrumbItems();
  const submitAction = useSubmitAction<ZaaktypeAction>(false);

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
    convertFieldsetsToTabConfig<TargetType>(fieldsets),
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
      payload: { serviceSlug: serviceSlug, zaaktype: result },
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
      const key = e.target.name as keyof typeof result;
      invariant(key in result, "key is not keyof result!");
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
        const objectKey = getObjectKey(originalValue);
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

    // First run deletions, this needs to run in a different request/transaction.
    await performAction({
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
              serviceSlug: serviceSlug,
              zaaktype: {
                ...(pendingUpdatesState || {}),
                uuid: conceptVersion?.uuid,
              },
            },
          },
          ...updates,
        ],
      },
    });
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
          serviceSlug: serviceSlug,
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
        serviceSlug: serviceSlug,
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

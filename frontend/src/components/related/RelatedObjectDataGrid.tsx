import {
  Button,
  DataGrid,
  FieldSet,
  Outline,
  SerializedFormData,
  TypedField,
  field2TypedField,
} from "@maykin-ui/admin-ui";
import { string2Title } from "@maykin-ui/client-common";
import { invariant } from "@maykin-ui/client-common/assert";
import { JSX, useCallback, useEffect, useMemo, useState } from "react";
import { flushSync } from "react-dom";
import { useNavigation, useParams } from "react-router";
import { SERVICE_PARAM } from "~/App.tsx";
import { TypedAction } from "~/hooks/useSubmitAction.tsx";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { Expand, Expanded, RelatedObject } from "~/types";

export type RelatedObjectDataGridProps<
  T extends { url: string },
  R extends object = RelatedObject<T>,
> = {
  /** Array of all fields available for `object`. */
  fields: TypedField[];
  /** FieldSet specifying which fields to include and their order. */
  fieldset: FieldSet<R>;
  /** Whether edit mode is active. */
  isEditing: boolean;
  /** The parent object for which related objects are displayed. */
  object: T;
  /** Key in the parent object representing the relationship. */
  relatedObjectKey: keyof Expand<Expanded<T>>;
  /** Initial array of related objects to display in the grid. */
  relatedObjects: R[];
  /** Called when list of actions (dispatch to persist) is changed. */
  onActionsChange: (actions: TypedAction<string, object>[]) => void;
  /**
   * Hook that allows modifying the `relatedObject` before committing changes.
   *
   * This function is called right before a change is committed, giving you a chance
   * to adjust or validate the `relatedObject`.
   *
   * @param relatedObject - The object related to the pending change.
   * @param actionType - The type of action describing the change.
   * @returns A promise resolving to either:
   * - The modified `relatedObject`, which will be committed.
   * - `false`, to cancel (skip) committing the change.
   *
   * If `false` is returned, the change will be discarded and not persisted.
   * If an updated object is returned, it will replace the original during commit.
   */
  hook?: (
    relatedObject: R,
    actionType: TypedAction<string, object>["type"],
    relatedObjectKey: keyof Expand<Expanded<T>>,
  ) => Promise<R | false>;
};

/**
 * A data grid for managing related objects of a parent object.
 *
 * Renders a table of related objects with configurable fields and fieldset.
 *
 * Supports adding, editing, and deleting rows while maintaining local mutation
 * and delete actions that can later be submitted to a backend.
 *
 * @typeParam T - The type of the parent object, which must include a `url` property.
 * @typeParam R - The type of the related object. Defaults to `RelatedObject<T>`.
 */
export function RelatedObjectDataGrid<
  T extends { url: string },
  R extends object = RelatedObject<T>,
>({
  fields,
  fieldset,
  isEditing: _isEditing,
  object,
  relatedObjectKey,
  relatedObjects,
  onActionsChange,
  hook = (row) => Promise.resolve(row),
}: RelatedObjectDataGridProps<T, R>) {
  // Loading state.
  const { state } = useNavigation();
  const isLoading = state !== "idle";

  // Route based params.
  const params = useParams();
  const serviceSlug = params[SERVICE_PARAM];
  invariant(serviceSlug, "serviceSlug must be provided!");

  // Whether edit mode is active.
  const [isEditing, setIsEditing] = useState(_isEditing);
  useEffect(() => {
    setIsEditing(_isEditing);
  }, [_isEditing]);

  // The fields included in the fieldset.
  const fieldSetFields = useMemo(
    () =>
      fieldset[1].fields.map(
        (fieldName) =>
          fields.find(
            (field) => field2TypedField<R>(field).name === fieldName,
          )!,
      ),
    [fieldset, fields],
  );

  // Typed fields, may contain overrides based on presentational need.
  // Expand name is normalized.
  const typedFields = useMemo<TypedField<R & { actions: JSX.Element }>[]>(
    () => [
      ...fieldSetFields.map((field) => ({
        ...field,
        editable: isEditing ? field.editable : false,
        name: String(field.name).split(".").pop() as keyof R,
        type: field.type === "text" ? "string" : field.type,
      })),
      { name: "actions", type: "jsx", editable: false, sortable: false },
    ],
    [fieldSetFields, isEditing],
  );

  // Delete actions state.
  const [deleteActions, setDeleteActions] = useState<
    TypedAction<string, object>[]
  >([]);

  // Mutation actions state.
  const [mutationActions, setMutationActions] = useState<
    (null | TypedAction<string, object>)[]
  >(new Array(relatedObjects.length).fill(null));

  // The object list state.
  const [objectList, setObjectList] = useState(relatedObjects);
  useEffect(() => {
    setObjectList(relatedObjects);
    setMutationActions(new Array(relatedObjects.length).fill(null));
    setDeleteActions([]);
  }, [relatedObjects, setObjectList, setMutationActions]);

  /**
   * Creates a new row object with default values based on the provided index.
   *
   * @param nextIndex - The sequential index used to generate default values.
   *
   * Behavior:
   * - If a field defines `options`, the value is chosen based on `nextIndex`
   *   (fallbacks to the first option if the index is out of range).
   * - Boolean fields default to `false`.
   * - Other fields get a descriptive string like `"FieldName 3"`.
   *
   * @returns A new object of type `R` representing a default-initialized row.
   */
  const createRow = useCallback(
    (nextIndex: number): R => {
      return typedFields.reduce<R>((acc, { name, type, options }) => {
        // Auto-pick option based on the next index, fallback to first option
        if (options) {
          const optionIndex = options[nextIndex - 1] ? nextIndex - 1 : 0;
          const value = options[optionIndex]?.value;
          return { ...acc, [name]: value };
        }

        // Default for booleans or fallback to descriptive string
        if (type === "boolean") {
          return { ...acc, [name]: false };
        }

        // Default descriptive string
        return {
          ...acc,
          [name]: `${string2Title(name as string)} ${nextIndex}`,
        };
      }, {} as R);
    },
    [typedFields],
  );

  /**
   * Finds the next available numeric index based on the current `objectList`.
   *
   * The function attempts to extract a trailing number from the `omschrijving`
   * or `volgnummer` fields of each row. If neither field contains a valid
   * number, the row’s position (1-based) is used instead.
   *
   * @returns The next available numeric index (starting at 1).
   */
  const findNextIndex = useCallback(() => {
    const usedIndices = objectList.map((row: R, i) => {
      // Try to extract a trailing number from `omschrijving`, e.g. "Item 3" → 3
      if ("omschrijving" in row) {
        const match = String(row.omschrijving).match(/\d+$/);
        if (match) {
          const int = parseInt(match[0]);
          return isNaN(int) ? i + 1 : int;
        }
      }

      // Otherwise, fall back to `volgnummer` if available
      if ("volgnummer" in row) {
        const int = parseInt(String(row.volgnummer));
        return isNaN(int) ? i + 1 : int;
      }

      // Default: use the row's position (1-based)
      return i + 1;
    });

    // Find the lowest unused positive index
    for (let i = 1; i <= usedIndices.length + 1; i++) {
      if (!usedIndices.includes(i)) return i;
    }

    // Fallback: just append at the end
    return usedIndices.length + 1;
  }, [objectList]);

  /**
   * Rejects a change after update is made within the DataGrid.
   *
   * This may be called when `hook()` returned falsy result and the change needs
   * to be discarded.
   *
   * We re-render the DataGrid with the old objectList after unsetting it
   * triggering internal side effects to accommodate input values.
   *
   * TODO: Investigate a better approach.
   */
  const rejectChange = useCallback(() => {
    const oldObjectList = [...objectList];
    const oldMutationActions = [...mutationActions];

    // flushSync explicitly prevents batched state updates here.
    flushSync(() => {
      setObjectList([]);
      setMutationActions([]);
    });

    flushSync(() => {
      setObjectList(() => oldObjectList);
      setMutationActions(() => oldMutationActions);
    });
  }, [objectList, setObjectList, mutationActions, setMutationActions]);

  /**
   * Adds a new row to the `objectList` and creates a corresponding action.
   *
   * Generates the next index using `findNextIndex()` and creates a new row
   * with `createRow()`. If the `"volgnummer"` field is included in
   * `fieldSetFields`, it sets the `volgnummer` property on the new row.
   *
   * Creates a new action of type `"ADD_RELATED_OBJECT"` with a payload
   * containing `serviceSlug`, `zaaktypeUuid`, `relatedObjectKey`, and
   * the new row. Updates both `objectList` and `actions` state accordingly.
   *
   * @remarks
   * - This function uses `useCallback` to memoize the handler.
   * - TypeScript expects a loosely typed new row; `@ts-expect-error` is used
   *   for `volgnummer` assignment.
   */
  const handleAdd = useCallback(async () => {
    const nextIndex = findNextIndex();
    const newRow = createRow(nextIndex);

    // Run hook.
    const rowWithHookResult = await hook(
      newRow,
      "ADD_RELATED_OBJECT",
      relatedObjectKey,
    );

    // Hook returned falsy result, reject change.,
    if (!rowWithHookResult) return;

    // Get field names.
    const fieldNames = fieldSetFields.map((field) =>
      String(field.name).split(".").pop(),
    );

    // Set index based volgnummer.
    if (fieldNames.includes("volgnummer")) {
      // @ts-expect-error - volgnummer assumed to be set on `R` when in `fieldSetFields`.
      rowWithHookResult["volgnummer"] = String(nextIndex);
    }

    // Create action.
    const addAction: TypedAction<string, object> = {
      type: "ADD_RELATED_OBJECT",
      payload: {
        serviceSlug: serviceSlug,
        zaaktypeUuid: getUUIDFromString(object.url as string) as string,
        relatedObjectKey: relatedObjectKey,
        relatedObject: rowWithHookResult,
      },
    };

    // Update State.
    const newObjectList = [...objectList, rowWithHookResult];
    const newMutationActions = [...mutationActions, addAction];
    setObjectList(newObjectList);
    setMutationActions(newMutationActions);

    const actions = [...deleteActions, ...newMutationActions].filter(
      (actionOrNull): actionOrNull is TypedAction<string, object> =>
        Boolean(actionOrNull),
    );
    onActionsChange(actions);
  }, [
    findNextIndex,
    createRow,
    hook,
    relatedObjectKey,
    fieldSetFields,
    setObjectList,
    objectList,
    setMutationActions,
    mutationActions,
    deleteActions,
    onActionsChange,
  ]);

  /**
   * Handles editing a specific row in the `objectList`.
   *
   * Finds the index of the provided `row` in `objectList` and updates the
   * corresponding action in the `actions` array. If an action exists at that
   * index, it updates its `payload.relatedObject` to the new row. If no action
   * exists, it creates a new action of type `"EDIT_RELATED_OBJECT"` with the
   * appropriate payload.
   *
   * @param row - The row from `objectList` that has been edited.
   *
   * @remarks
   * Updates `actions` state using `setActions`. Currently, note that this
   * logic may not correctly trigger re-renders if `objectList` items are
   * objects and strict equality (`===`) is used for comparison.
   */
  const handleEdit = useCallback(
    async (row: SerializedFormData) => {
      // Find row index.
      const index = displayedObjectList.findIndex((object) => object === row);

      // Clean object.
      const _relatedObject = { ...row };
      delete _relatedObject.actions;
      const relatedObject = _relatedObject as R;

      // Run hook.
      const rowWithHookResult = await hook(
        relatedObject,
        "EDIT_RELATED_OBJECT",
        relatedObjectKey,
      );

      // Hook returned falsy result, reject change.,
      if (!rowWithHookResult) {
        rejectChange();
        return;
      }

      const newObjectList = objectList.map((row, i) =>
        index === i ? (rowWithHookResult as R) : row,
      );

      const newMutationActions = mutationActions.map((action, i) => {
        if (i === index) {
          return action
            ? {
                ...action,
                payload: {
                  ...action.payload,
                  relatedObject: rowWithHookResult,
                },
              }
            : {
                type: "EDIT_RELATED_OBJECT",
                payload: {
                  serviceSlug: serviceSlug,
                  zaaktypeUuid: getUUIDFromString(
                    object.url as string,
                  ) as string,
                  relatedObjectKey,
                  relatedObject: rowWithHookResult,
                },
              };
        }
        return action;
      });

      setObjectList(newObjectList);
      setMutationActions(newMutationActions);

      const actions = [...deleteActions, ...newMutationActions].filter(
        (actionOrNull): actionOrNull is TypedAction<string, object> =>
          Boolean(actionOrNull),
      );
      onActionsChange(actions);
    },
    [
      objectList,
      hook,
      relatedObjectKey,
      rejectChange,
      mutationActions,
      setObjectList,
      setMutationActions,
      deleteActions,
      onActionsChange,
    ],
  );

  /**
   * Deletes a row from the `objectList` and its corresponding action.
   *
   * Finds the index of the given `row` in `objectList` using strict equality (`===`),
   * then removes the row from `objectList` and the action at the same index from `actions`.
   *
   * @param row - The row to delete from the object list.
   *
   * @remarks
   * - Uses `useCallback` to memoize the handler.
   * - Deletion relies on object reference equality. If the `row` reference does not match
   *   an object in `objectList`, no deletion occurs.
   */
  const handleDelete = useCallback(
    async (row: R) => {
      const index = objectList.findIndex(
        (object: (typeof objectList)[number]) => object === row,
      );

      // Run hook.
      const rowWithHookResult = await hook(
        row,
        "DELETE_RELATED_OBJECT",
        relatedObjectKey,
      );

      // Hook returned falsy result, reject change.,
      if (!rowWithHookResult) {
        rejectChange();
        return;
      }

      setObjectList(objectList.filter((_, i) => i !== index));
      setMutationActions(mutationActions.filter((_, i) => i !== index));

      // Whether the removed item is frontend only (and not yet persisted to the backend).
      // This is determined based on the (presence) of an action with type "ADD_RELATED_OBJECT").
      const isStub = mutationActions[index]?.type === "ADD_RELATED_OBJECT";

      // If the removed item is not a stub, create a separate action for the removal.
      if (!isStub) {
        invariant(
          "uuid" in rowWithHookResult,
          "rowWithHookResult does not contain uuid field!",
        );
        const deleteAction: TypedAction<string, object> = {
          type: "DELETE_RELATED_OBJECT",
          payload: {
            serviceSlug: serviceSlug,
            zaaktypeUuid: getUUIDFromString(object.url as string) as string,
            relatedObjectKey: relatedObjectKey,
            relatedObjectUuid: rowWithHookResult.uuid,
          },
        };

        const newDeleteActions = [...deleteActions, deleteAction];
        setDeleteActions(newDeleteActions);

        const actions = [...newDeleteActions, ...mutationActions].filter(
          (actionOrNull): actionOrNull is TypedAction<string, object> =>
            Boolean(actionOrNull),
        );
        onActionsChange(actions);
      }
    },
    [
      objectList,
      setObjectList,
      setMutationActions,
      mutationActions,
      setDeleteActions,
      deleteActions,
      onActionsChange,
    ],
  );

  // The objects to render, may include overrides and actions.
  const displayedObjectList = useMemo<(R & { actions: JSX.Element })[]>(() => {
    return objectList.map((row) => {
      const overrides: Partial<R> = {};
      if (!isEditing) {
        for (const key in row) {
          const field = typedFields.find(
            (typedFields) => typedFields.name === key,
          );
          const options = field?.options;
          if (!options) continue;

          const value = row[key];
          const option = options.find((option) => option.value === value);
          if (!option) continue;

          // @ts-expect-error - R[key] may not be string.
          overrides[key] = option.label;
        }
      }

      return {
        ...row,
        ...overrides,
        actions: (
          <Button
            disabled={isLoading || !isEditing}
            size="xs"
            variant="danger"
            title="Verwijderen"
            onClick={() => handleDelete(row)}
          >
            <Outline.TrashIcon />
          </Button>
        ),
      };
    });
  }, [objectList, isEditing, typedFields]);

  // `objectList[index]` action should be resolvable by `actions[index]` an be
  // either a `TypedAction` or `null`.
  invariant(
    objectList.length === mutationActions.length,
    "objectList and mutationActions should be in sync!",
  );

  return (
    <>
      <DataGrid<R & { actions: JSX.Element }>
        editable={isEditing}
        editing={isEditing}
        decorate
        fields={typedFields}
        urlFields={[]}
        objectList={displayedObjectList}
        sort
        onEdit={handleEdit}
      />

      {isEditing && (
        <Button disabled={isLoading} variant="secondary" onClick={handleAdd}>
          <Outline.PlusIcon />
          Voeg toe
        </Button>
      )}
    </>
  );
}

import {
  Button,
  DataGrid,
  Field,
  Outline,
  SerializedFormData,
  Toolbar,
  TypedField,
} from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import { JSX, useCallback, useEffect, useMemo, useState } from "react";
import { flushSync } from "react-dom";
import { useNavigation, useParams } from "react-router";
import { SERVICE_PARAM } from "~/App.tsx";
import { Errors } from "~/hooks";

export type RelatedObjectDataGridAction<T extends object> =
  | RelatedObjectDataGridCreateAction<T>
  | RelatedObjectDataGridUpdateAction<T>
  | RelatedObjectDataGridDeleteAction<T>;

export type RelatedObjectDataGridCreateAction<T extends object> = {
  type: "CREATE";
  payload: RelatedObjectDataGridDeletePayload<T>;
};

export type RelatedObjectDataGridUpdateAction<T extends object> = {
  type: "UPDATE";
  payload: RelatedObjectDataGridDeletePayload<T>;
};

export type RelatedObjectDataGridDeleteAction<T extends object> = {
  type: "DELETE";
  payload: RelatedObjectDataGridDeletePayload<T>;
};

export type RelatedObjectDataGridDeletePayload<T extends object> = {
  rowIndex: number;
  object: T;
};

export type RelatedObjectDataGridProps<T extends object> = {
  /** The errors rows to show. */
  errors: Errors[];
  /** The fields to show. */
  fields: (Field | TypedField)[];
  /** Whether edit mode is active. */
  isEditing: boolean;
  /** Initial array of objects to display in the grid. */
  objectList: T[];
  /** Called when list of actions (dispatch to persist) is changed. */
  onActionsChange: (actions: RelatedObjectDataGridAction<T>[]) => void;
  /**
   * Hook that allows modifying the `relatedObject` before committing changes. Can be called directly by the user using
   * an action button, if this button is used: `hook` will be called with `userRequested` set to true..
   *
   * This function is called right before a change is committed, giving you a chance
   * to adjust or validate the `relatedObject`.
   *
   * @param object - The object related to the pending change.
   * @param actionType - The type of action describing the change.
   * @param userRequested - Whether the user explicitly triggered the hook.
   * @returns A promise resolving to either:
   * - The modified `object`, which will be committed.
   * - `false`, to cancel (skip) committing the change.
   *
   * If `false` is returned, the change will be discarded and not persisted.
   * If an updated object is returned, it will replace the original during commit.
   */
  hook?: (
    object: T,
    actionType: RelatedObjectDataGridAction<T>["type"],
    userRequested: boolean,
  ) => Promise<T | false>;
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
export function RelatedObjectDataGrid<T extends object = object>({
  errors,
  fields,
  isEditing,
  objectList,
  onActionsChange,
  hook = (row) => Promise.resolve(row),
}: RelatedObjectDataGridProps<T>) {
  // Loading state.
  const { state } = useNavigation();
  const isLoading = state !== "idle";

  // Route based params.
  const params = useParams();
  const serviceSlug = params[SERVICE_PARAM];
  invariant(serviceSlug, "serviceSlug must be provided!");

  // Whether edit mode is active.
  const [isEditingState, setIsEditingState] = useState(isEditing);
  useEffect(() => {
    setIsEditingState(isEditing);
  }, [isEditing]);

  // Typed fields, may contain overrides based on presentational need.
  // Expand name is normalized.
  const typedFields = useMemo<TypedField<T & { actions: JSX.Element }>[]>(
    () => [
      ...fields.map((field) => ({
        ...field,
        editable: isEditingState ? field.editable : false,
        name: String(field.name).split(".").pop() as keyof T,
        type: field.type === "text" ? "string" : field.type,
      })),
      { name: "actions", type: "jsx", editable: false, sortable: false },
    ],
    [fields, isEditingState],
  );

  // Add actions state.
  const [createActionsState, setCreateActionsState] = useState<
    RelatedObjectDataGridCreateAction<T>[]
  >([]);

  // Mutation actions state.
  const [updateActionsState, setUpdateActionsState] = useState<
    (null | RelatedObjectDataGridUpdateAction<T>)[]
  >(new Array(objectList.length).fill(null));

  // Delete actions state.
  const [deleteActionsState, setDeleteActionsState] = useState<
    RelatedObjectDataGridDeleteAction<T>[]
  >([]);

  // The object list state.
  const [objectListState, setObjectListState] = useState(objectList);
  useEffect(() => {
    setObjectListState([...objectList]);
    setCreateActionsState([]);
    setUpdateActionsState(new Array(objectList.length).fill(null));
    setDeleteActionsState([]);
  }, [JSON.stringify(objectList)]);

  /**
   * Creates a new row object with default values based on the provided index.
   **
   * Behavior:
   * - Boolean fields default to `false`.
   * - Other fields get an empty string.
   *
   * @returns A new object of type `T` representing a default-initialized row.
   */
  const createRow = useCallback((): T => {
    return typedFields.reduce<T>((acc, { name, type }) => {
      // Default for booleans or fallback to descriptive string
      if (type === "boolean") {
        return { ...acc, [name]: false };
      }

      // Default descriptive string
      return {
        ...acc,
        [name]: ``,
      };
    }, {} as T);
  }, [typedFields]);

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
    const usedIndices = objectListState.map((row: T, i) => {
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
  }, [objectListState]);

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
    const oldObjectList = [...objectListState];
    const oldUpdateActions = [...updateActionsState];

    // flushSync explicitly prevents batched state updates here.
    flushSync(() => {
      setObjectListState([]);
      setUpdateActionsState([]);
    });

    flushSync(() => {
      setObjectListState(() => oldObjectList);
      setUpdateActionsState(() => oldUpdateActions);
    });
  }, [objectListState, updateActionsState]);

  /**
   * Adds a new row to the `objectList` and creates a corresponding action.
   *
   * Generates the next index using `findNextIndex()` and creates a new row
   * with `createRow()`. If the `"volgnummer"` field is included in
   * `fieldSetFields`, it sets the `volgnummer` property on the new row.
   *
   * Creates a new action of type `"CREATE"`, and the new row.
   * Updates both `objectList` and `actions` state accordingly.
   *
   * @remarks
   * - This function uses `useCallback` to memoize the handler.
   * - TypeScript expects a loosely typed new row; `@ts-expect-error` is used
   *   for `volgnummer` assignment.
   */
  const handleCreate = useCallback(async () => {
    const nextIndex = findNextIndex();
    const newRow = createRow();

    // Run hook.
    const rowWithHookResult = await hook(newRow, "CREATE", false);

    // Hook returned falsy result, reject change.,
    if (!rowWithHookResult) return;

    // Get field names.
    const fieldNames = fields.map((field) =>
      String(field.name).split(".").pop(),
    );

    // Set index based volgnummer.
    if (fieldNames.includes("volgnummer")) {
      // @ts-expect-error - volgnummer assumed to be set on `T` when in `fieldSetFields`.
      rowWithHookResult["volgnummer"] = String(nextIndex);
    }

    // Create action.
    const addAction: RelatedObjectDataGridAction<T> = {
      type: "CREATE",
      payload: { rowIndex: objectListState.length, object: rowWithHookResult },
    };

    // Update State.
    const newObjectList = [...objectListState, rowWithHookResult];
    const newAddActions = [...createActionsState, addAction];
    setObjectListState(newObjectList);
    setCreateActionsState(newAddActions);

    const actions = [
      ...deleteActionsState,
      ...updateActionsState,
      ...newAddActions,
    ].filter((actionOrNull): actionOrNull is RelatedObjectDataGridAction<T> =>
      Boolean(actionOrNull),
    );
    onActionsChange(actions);
  }, [
    findNextIndex,
    createRow,
    hook,
    objectListState,
    createActionsState,
    updateActionsState,
    deleteActionsState,
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
      const relatedObject = _relatedObject as T;

      // Run hook.
      const rowWithHookResult = await hook(relatedObject, "UPDATE", false);

      // Hook returned falsy result, reject change.,
      if (!rowWithHookResult) {
        rejectChange();
        return;
      }

      const newObjectList = objectListState.map((row, i) =>
        index === i ? (rowWithHookResult as T) : row,
      );

      // Update `updateActions` for existing object.
      const newUpdateActions =
        index <= updateActionsState.length - 1
          ? updateActionsState.map((action, i) => {
              if (i === index) {
                return {
                  ...action,
                  type: "UPDATE" as const,
                  payload: {
                    rowIndex: index,
                    object: rowWithHookResult,
                  },
                };
              }
              return action;
            })
          : updateActionsState;

      // Update `addActions` for newly created object.
      const newAddActions =
        index > updateActionsState.length - 1
          ? createActionsState.map((action, i) => {
              if (i + updateActionsState.length === index) {
                return {
                  ...action,
                  payload: { rowIndex: index, object: rowWithHookResult },
                };
              }
              return action;
            })
          : createActionsState;

      setObjectListState(newObjectList);
      setUpdateActionsState(newUpdateActions);
      setCreateActionsState(newAddActions);

      const actions = [
        ...deleteActionsState,
        ...newUpdateActions,
        ...newAddActions,
      ].filter((actionOrNull): actionOrNull is RelatedObjectDataGridAction<T> =>
        Boolean(actionOrNull),
      );
      onActionsChange(actions);
    },
    [
      objectListState,
      hook,
      rejectChange,
      createActionsState,
      updateActionsState,
      deleteActionsState,
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
    async (row: T) => {
      const index = objectListState.findIndex(
        (object: (typeof objectListState)[number]) => object === row,
      );

      // Run hook.
      const rowWithHookResult = await hook(row, "DELETE", false);

      // Hook returned falsy result, reject change.,
      if (!rowWithHookResult) {
        rejectChange();
        return;
      }

      setObjectListState(objectListState.filter((_, i) => i !== index));
      setUpdateActionsState(updateActionsState.filter((_, i) => i !== index));
      setCreateActionsState(
        createActionsState.filter(
          (_, i) => i + updateActionsState.length !== index,
        ),
      );

      // Whether the removed item is frontend only (and not yet persisted to the backend).
      // This is determined based on the (presence) of an action with type "CREATE").
      const isStub =
        [...updateActionsState, ...createActionsState][index]?.type ===
        "CREATE";

      // If the removed item is not a stub, create a separate action for the removal.
      if (!isStub) {
        invariant(
          "uuid" in rowWithHookResult,
          "rowWithHookResult does not contain uuid field!",
        );
        const deleteAction: RelatedObjectDataGridAction<T> = {
          type: "DELETE",
          payload: { rowIndex: index, object: rowWithHookResult },
        };

        const newDeleteActions = [...deleteActionsState, deleteAction];
        setDeleteActionsState(newDeleteActions);

        const actions = [
          ...newDeleteActions,
          ...updateActionsState,
          ...createActionsState,
        ].filter(
          (actionOrNull): actionOrNull is RelatedObjectDataGridAction<T> =>
            Boolean(actionOrNull),
        );
        onActionsChange(actions);
      }
    },
    [
      objectListState,
      createActionsState,
      updateActionsState,
      deleteActionsState,
      onActionsChange,
    ],
  );

  /**
   * Manually executes the optional `hook` for a row triggered by a user action.
   *
   * Behaviour:
   * - locates the row by reference in `objectListState`
   * - calls `hook()` with action type `"UPDATE"` and `userRequested = true`
   * - if `hook` returns `false` the change is ignored
   * - if `hook` returns an updated object it is committed as update action
   *
   * @param row - The row for which the hook should be executed.
   */
  const handleHook = useCallback(
    async (row: object) => {
      // Find row index.
      const index = objectListState.findIndex((object) => object === row);

      // Clean object.
      const _relatedObject = { ...row };
      if ("actions" in _relatedObject) {
        delete _relatedObject.actions;
      }
      const relatedObject = _relatedObject as T;

      // Run hook.
      const rowWithHookResult = await hook(relatedObject, "UPDATE", true);

      if (!rowWithHookResult) {
        return;
      }

      const newObjectList = objectListState.map((row, i) =>
        index === i ? (rowWithHookResult as T) : row,
      );

      // Update `updateActions` for existing object.
      const newUpdateActions =
        index <= updateActionsState.length - 1
          ? updateActionsState.map((action, i) => {
              if (i === index) {
                return {
                  ...action,
                  type: "UPDATE" as const,
                  payload: {
                    rowIndex: index,
                    object: rowWithHookResult,
                  },
                };
              }
              return action;
            })
          : updateActionsState;

      // Update `addActions` for newly created object.
      const newAddActions =
        index > updateActionsState.length - 1
          ? createActionsState.map((action, i) => {
              if (i + updateActionsState.length === index) {
                return {
                  ...action,
                  payload: { rowIndex: index, object: rowWithHookResult },
                };
              }
              return action;
            })
          : createActionsState;

      setObjectListState(newObjectList);
      setUpdateActionsState(newUpdateActions);
      setCreateActionsState(newAddActions);

      const actions = [
        ...deleteActionsState,
        ...newUpdateActions,
        ...newAddActions,
      ].filter((actionOrNull): actionOrNull is RelatedObjectDataGridAction<T> =>
        Boolean(actionOrNull),
      );
      onActionsChange(actions);
    },
    [
      objectListState,
      hook,
      createActionsState,
      updateActionsState,
      deleteActionsState,
      onActionsChange,
    ],
  );

  // The objects to render, may include overrides and actions.
  const displayedObjectList = useMemo<(T & { actions: JSX.Element })[]>(() => {
    return objectListState.map((row) => {
      const overrides: Partial<T> = {};
      if (!isEditingState) {
        for (const key in row) {
          const field = typedFields.find(
            (typedFields) => typedFields.name === key,
          );
          const options = field?.options;
          if (!options || typeof options === "function") continue;

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
          <Toolbar pad={false}>
            <Button
              disabled={isLoading || !isEditingState}
              title="Meer velden"
              onClick={() => handleHook(row)}
            >
              <Outline.SquaresPlusIcon />
            </Button>
            <Button
              disabled={isLoading || !isEditingState}
              variant="danger"
              title="Verwijderen"
              onClick={() => handleDelete(row)}
            >
              <Outline.TrashIcon />
            </Button>
          </Toolbar>
        ),
      };
    });
  }, [objectListState, isEditingState, typedFields]);

  // Every item in `objectList` should have a record in [...updateActions, ...addActions], in other words:
  // every row has an actions (or null) attached to it based on its index.
  // This makes sure the list does not get out of sync.
  invariant(
    objectListState.length ===
      updateActionsState.length + createActionsState.length,
    "objectList and updateActions should be in sync!",
  );

  return (
    <>
      <DataGrid<T & { actions: JSX.Element }>
        editable={isEditingState}
        editing={isEditingState}
        errors={errors}
        decorate
        fields={typedFields}
        urlFields={[]}
        objectList={displayedObjectList}
        sort
        onEdit={handleEdit}
      />

      {isEditingState && (
        <Button disabled={isLoading} variant="secondary" onClick={handleCreate}>
          <Outline.PlusIcon />
          Voeg toe
        </Button>
      )}
    </>
  );
}

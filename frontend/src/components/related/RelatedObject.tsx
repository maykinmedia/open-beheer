import {
  Button,
  DataGrid,
  Field,
  Outline,
  TypedField,
  field2TypedField,
  fields2TypedFields,
} from "@maykin-ui/admin-ui";
import { string2Title } from "@maykin-ui/client-common";
import { invariant } from "@maykin-ui/client-common/assert";
import {
  Ref,
  forwardRef,
  useEffect,
  useImperativeHandle,
  useMemo,
  useState,
} from "react";
import { useNavigation, useParams } from "react-router";
import { SERVICE_PARAM } from "~/App.tsx";
import { RelatedObjectBadge } from "~/components/related/RelatedObjectBadge.tsx";
import { useCombinedSearchParams } from "~/hooks";
import { TypedAction } from "~/hooks/useSubmitAction.tsx";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { TabConfig, TargetType } from "~/pages";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { ExpandItemKeys, RelatedObject, components } from "~/types";

/**
 * This refers to the fields in an object which are allowed to be rendered for
 * an related object. If none of those match: an attempt is made to automatically
 * find candidates.
 */
const DEFAULT_ALLOWED_FIELDS = [
  "procestype",
  "naam",
  "omschrijving",
  "objecttype",
];

const SYMBOL_STUB_KEY = Symbol(
  "SYMBOL_STUB_KEY, used to identify the position of the stub in `rows`",
);
const SYMBOL_ROW_ACTION = Symbol(
  "SYMBOL_STUB_ACTION, set to action required to make the wanted changes to the row",
);

type RelatedRow<T extends object> = (RelatedObject<T> extends Array<T>
  ? RelatedObject<T>[number]
  : RelatedObject<T>) & {
  [SYMBOL_STUB_KEY]?: string;
  [SYMBOL_ROW_ACTION]?: TypedAction;
};

/**
 * Props for the {@link RelatedObjectRenderer} component.
 *
 * @typeParam T - The base object type for which related objects are expanded.
 */
type RelatedObjectRendererProps<T extends TargetType> = {
  object: T;
  /** The related object(s) to display or edit. */
  relatedObject: RelatedObject<T>;
  /** The type of view to render (e.g., "DataGrid" or "AttributeGrid"). */
  view: TabConfig<T>["view"];
  /** The specific expanded field key. */
  field: ExpandItemKeys<T>;
  /** Possible fields. */
  fields: components["schemas"]["OBField"][];
  /** The set of fields to expand and render. */
  expandFields?: Array<Field<T> | TypedField<T>>;
};

export type RelatedObjectRendererHandle = {
  /** Returns a list of actions to perform when saving. */
  getSaveActions: () => ZaaktypeAction[];

  /** Cancels planned changes. */
  cancel: () => void;
};

/**
 * Renders either a DataGrid or a list of badges for a set of related objects,
 * depending on the tab configuration.
 */
export const RelatedObjectRenderer = forwardRef(
  <T extends TargetType>(
    props: RelatedObjectRendererProps<T>,
    ref: Ref<RelatedObjectRendererHandle>,
  ) => {
    const {
      expandFields: _expandFields,
      field,
      fields,
      object,
      relatedObject,
      view,
    } = props;

    // WHen expandFields is not explicitly set, resolve it by finding all text fields
    // that start with the "_expand." prefix followed by the name of the field.
    // The value is used to determine:
    //
    // - What field names to allow as representation for an related object (after
    //    stripping "expand." prefix) in "AttributeGrid" presentation.
    //
    // - What fields to render in "DataGrid" presentation.
    const expandFields = _expandFields
      ? fields2TypedFields(_expandFields)
      : (fields
          .filter((f) => f.type === "string" || f.type === "text")
          .filter((f) => f.name !== "url")
          .filter((f) =>
            f.name.startsWith("_expand." + field),
          ) as TypedField[]);

    // This refers to the fields in an object which are allowed to be rendered for
    // an related object.
    // and required stripping "expand." prefix.
    //
    // To prevent unwanted results; DEFAULT_ALLOWED_FIELDS are always favored.
    // and other field names bound to the related object acts as fallback.
    const fallbackAllowedFields = expandFields.map(
      (f) => f.name.toString().split(".").pop()!,
    );
    const allowedFields = [
      ...DEFAULT_ALLOWED_FIELDS,
      ...fallbackAllowedFields,
    ] as unknown as ExpandItemKeys<T>[];

    useImperativeHandle<
      RelatedObjectRendererHandle,
      RelatedObjectRendererHandle
    >(ref, () => ({
      /** Returns a list of actions to perform when saving. */
      getSaveActions() {
        invariant(serviceSlug, "serviceSlug must be provided!");
        return [
          ...deleteActions,
          ...rows.map((row) => row[SYMBOL_ROW_ACTION]).filter(Boolean),
        ];
      },

      cancel() {
        setRows(Array.isArray(relatedObject) ? relatedObject : [relatedObject]);
      },
    }));

    const [combinedSearchParams] = useCombinedSearchParams();
    const isEditing = Boolean(combinedSearchParams.get("editing"));
    invariant("url" in object, "object should have url!");
    const zaaktypeUuid = getUUIDFromString(object.url as string);

    const params = useParams();
    const serviceSlug = params[SERVICE_PARAM];
    invariant(serviceSlug, "serviceSlug must be provided!");

    const { state } = useNavigation();
    const isLoading = state !== "idle";

    // Contains related object as well as their mutating action.
    const [rows, setRows] = useState<RelatedRow<T>[]>(
      Array.isArray(relatedObject) ? relatedObject : [relatedObject],
    );
    useEffect(() => {
      setRows(Array.isArray(relatedObject) ? relatedObject : [relatedObject]);
      setDeleteActions([]);
    }, [relatedObject]);

    // Deletions as actions, other actions are stored on rows.
    const [deleteActions, setDeleteActions] = useState<TypedAction[]>([]);

    const expandFieldsNames = expandFields.map(
      (expandField) => expandField.name,
    ) as string[]; // FIXME

    const typedFields = fields
      .filter((field) => expandFieldsNames.includes(field.name))
      .map((field) => {
        const name = field.name;
        const shortName = name.includes(".")
          ? (name.split(".").pop() as keyof T)
          : name;

        const typedField = field2TypedField(field as TypedField<T>, undefined);
        typedField.editable = isEditing ? typedField.editable : false;
        typedField.name = shortName as keyof T;
        return typedField;
      });
    const fieldNames = typedFields.map((t) => t.name);

    /**
     * Handles adding a new related object stub with default values.
     * Ensures that numeric fields like `volgnummer` are incremented.
     */
    const handleAdd = () => {
      invariant(rows, "rows is undefined!");
      invariant(Array.isArray(rows), "rows must be Array!");

      // Get the indices currently in use.
      const usedIndices = rows.map((r, i) => {
        const match = r.omschrijving?.match(/\d+$/); // Match number at end.
        if (match) {
          return parseInt(match[0]);
        }
        return parseInt(r.volgnummer) || i;
      });

      // Find the next index.
      let nextIndex = 1;
      for (let i = 1; i <= rows.length + 1; i++) {
        if (usedIndices.includes(i)) continue;
        nextIndex = i;
        break;
      }

      const relatedObjectStub = typedFields.reduce<RelatedRow<T>>(
        (acc, { name, type, options }) => {
          let value;

          // Auto pick option based on index.
          if (options?.length) {
            value = options[nextIndex - 1]
              ? options[nextIndex - 1].value
              : options[0].value;
          } else {
            // Default value for boolean.
            switch (type) {
              case "boolean":
                value = false;
                break;
              // Default behavior based on name.
              default:
                value = `${string2Title(name as string)} ${nextIndex}`;
            }
          }

          return {
            ...acc,
            [name]: value,
          };
        },
        {},
      );

      // @ts-expect-error - Loosely typed.
      if (fieldNames.includes("volgnummer")) {
        relatedObjectStub["volgnummer"] = String(nextIndex);
      }

      relatedObjectStub[SYMBOL_STUB_KEY] = nextIndex;
      relatedObjectStub[SYMBOL_ROW_ACTION] = {
        type: "ADD_RELATED_OBJECT",
        payload: {
          serviceSlug: serviceSlug,
          zaaktypeUuid: zaaktypeUuid,
          relatedObjectKey: field,
          relatedObject: relatedObjectStub,
        },
      };
      setRows([...rows, relatedObjectStub]);
    };

    /**
     * Handles editing an existing related object.
     *
     * @param relatedRow - The related row.
     */
    const handleEdit = (relatedRow: RelatedRow<T>) => {
      const isStub = SYMBOL_STUB_KEY in relatedRow;
      // If `relatedObject` is a stub, edit the state.
      if (isStub) {
        const currentAction = relatedRow[SYMBOL_ROW_ACTION];
        currentAction.payload.relatedObject = relatedRow;

        const newRows = rows.map((row) =>
          row[SYMBOL_STUB_KEY] === relatedRow[SYMBOL_STUB_KEY]
            ? relatedRow
            : row,
        );

        setRows(newRows);
        return;
      }

      setRows(
        rows.map((row) =>
          row[SYMBOL_STUB_KEY] === relatedRow[SYMBOL_STUB_KEY]
            ? {
                ...row,
                [SYMBOL_ROW_ACTION]: {
                  type: "EDIT_RELATED_OBJECT",
                  payload: {
                    serviceSlug: serviceSlug,
                    zaaktypeUuid: zaaktypeUuid,
                    relatedObjectKey: field,
                    relatedObject: relatedRow,
                  },
                },
              }
            : row,
        ),
      );
    };

    /**
     * Handles deleting a related object.
     *
     * @param relatedRow - The related row.
     */
    const handleDelete = (relatedRow: RelatedRow<T>) => {
      const relatedRowUuid = getUUIDFromString(
        relatedRow.uuid || relatedRow.url || "",
      );

      const isStub = SYMBOL_STUB_KEY in relatedRow;
      setRows(rows.filter((r) => r !== relatedRow));

      // If `relatedObject` is not a stub, create delete action.
      if (!isStub) {
        invariant(
          relatedRowUuid,
          "either relatedRow.uuid or relatedRow.url must be set",
        );
        const action = {
          type: "DELETE_RELATED_OBJECT",
          payload: {
            serviceSlug: serviceSlug,
            zaaktypeUuid: zaaktypeUuid,
            relatedObjectKey: field,
            relatedObjectUuid: relatedRowUuid,
          },
        };
        setDeleteActions([...deleteActions, action]);
      }
    };

    /**
     * A memoized list of related objects augmented with action buttons
     * (e.g., a delete button).
     */
    const augmentedObjectList = useMemo(
      () =>
        Array.isArray(rows)
          ? rows
              .map((row) => ({
                ...row,
                "": (
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
              }))
              .filter(
                (r) => r[SYMBOL_ROW_ACTION]?.type !== "DELETE_RELATED_OBJECT",
              )
          : [],
      [rows, isLoading, isEditing],
    );

    // Single related item in AttributeList.
    if (view === "AttributeGrid" && !Array.isArray(relatedObject)) {
      if (!relatedObject) return null;

      return (
        <RelatedObjectBadge
          relatedObject={relatedObject}
          allowedFields={allowedFields}
        />
      );
    }

    // Multiple related items in AttributeList.
    if (view === "AttributeGrid" && Array.isArray(relatedObject)) {
      return relatedObject.map((relatedObject, index) => (
        <RelatedObjectBadge
          key={relatedObject.uuid ?? index}
          relatedObject={relatedObject}
          allowedFields={allowedFields}
        />
      ));
    }

    // DataGrid view.
    if (view === "DataGrid" && Array.isArray(relatedObject)) {
      return (
        <>
          <DataGrid<(typeof relatedObject)[number]>
            objectList={augmentedObjectList}
            fields={[
              ...typedFields,
              { name: "", type: "jsx", editable: false, sortable: false },
            ]}
            boolProps={{ explicit: true }}
            decorate
            editable={isEditing}
            editing={isEditing}
            sort={
              augmentedObjectList.length &&
              "volgnummer" in augmentedObjectList[0]
                ? "volgnummer"
                : undefined
            }
            onEdit={(data) => {
              delete data[""]; // Action column.
              handleEdit(data as RelatedObject<T>);
            }}
            urlFields={[]}
          />

          {isEditing && (
            <Button
              disabled={isLoading}
              variant="secondary"
              onClick={handleAdd}
            >
              <Outline.PlusIcon />
              Voeg toe
            </Button>
          )}
        </>
      );
    }
  },
);
RelatedObjectRenderer.displayName = "RelatedObjectRenderer";

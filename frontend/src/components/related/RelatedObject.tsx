import { Button, DataGrid, Outline, TypedField } from "@maykin-ui/admin-ui";
import { string2Title } from "@maykin-ui/client-common";
import { invariant } from "@maykin-ui/client-common/assert";
import { useMemo } from "react";
import { useNavigation, useParams } from "react-router";
import { SERVICE_PARAM } from "~/App.tsx";
import { RelatedObjectBadge } from "~/components/related/RelatedObjectBadge.tsx";
import { useCombinedSearchParams } from "~/hooks";
import { useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import { getZaaktypeUUID } from "~/lib";
import { BaseTabSection, TabConfig } from "~/pages";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { ExpandItemKeys, RelatedObject, components } from "~/types";

/**
 * Props for the {@link RelatedObjectRenderer} component.
 *
 * @typeParam T - The base object type for which related objects are expanded.
 */
type RelatedObjectRendererProps<T extends object> = {
  /** The related object(s) to display or edit. */
  relatedObject: RelatedObject<T>;
  /** The type of view to render (e.g., "DataGrid" or "AttributeGrid"). */
  view: TabConfig<T>["view"];
  /** The set of fields to expand and render. */
  expandFields: BaseTabSection<T>["expandFields"];
  /** The specific expanded field key. */
  field: ExpandItemKeys<T>;
  /** UUID of the zaaktype the related object belongs to. */
  zaaktypeUuid: string;
  fields: components["schemas"]["OBField"][];
};

/**
 * Renders either a DataGrid or a list of badges for a set of related objects,
 * depending on the tab configuration.
 *
 * @param relatedObject - The array or single object to render
 * @param view - The view type, either "DataGrid" or "AttributeGrid"
 * @param expandFields - The set of fields to expand and show
 * @param field - The expanded field key for the related object(s)
 * @param zaaktypeUuid - UUID of the zaaktype the related object is tied to
 */
export function RelatedObjectRenderer<T extends object>({
  relatedObject,
  view,
  expandFields,
  field,
  zaaktypeUuid,
  fields,
}: RelatedObjectRendererProps<T>) {
  const params = useParams();
  const submitAction = useSubmitAction<ZaaktypeAction>();

  const [combinedSearchParams] = useCombinedSearchParams();
  const isEditing = Boolean(combinedSearchParams.get("editing"));

  const serviceSlug = params[SERVICE_PARAM];
  invariant(serviceSlug, "serviceSlug must be provided!");

  const { state } = useNavigation();
  const isLoading = state !== "idle";

  const expandFieldsNames = expandFields.map((expandField) => {
    if (typeof expandField === "string") {
      return expandField;
    } else {
      return expandField.name;
    }
  });

  const typedFields = fields
    .filter((backendField) => expandFieldsNames.includes(backendField.name))
    .map((backendField) => {
      // The expandFields can be either strings (just the name of the field to show) or objects, with
      // more configurations for the field.
      const frontendExtras = expandFields.find(
        (expandField) =>
          typeof expandField !== "string" &&
          expandField.name === backendField.name,
      ) as TypedField<RelatedObject<T>> | undefined;

      const fieldPrefix = `_expand.${field}.`;
      return {
        ...frontendExtras,
        ...backendField,
        // We removed the prefix, so now the keys are fields of the expanded object.
        name: backendField.name.replace(fieldPrefix, "") as ExpandItemKeys<T>,
      };
    });

  const fieldNames = typedFields.map((t) => t.name);

  /**
   * Handles adding a new related object stub with default values.
   * Ensures that numeric fields like `volgnummer` are incremented.
   */
  const handleAdd = () => {
    invariant(Array.isArray(relatedObject), "relatedObject must be Array!");
    invariant(relatedObject, "relatedObject is undefined!");

    // Get the indices currently in use.
    const usedIndices = relatedObject.map((r, i) => {
      const match = r.omschrijving?.match(/\d+$/); // Match number at end.
      if (match) {
        return parseInt(match[0]);
      }
      return parseInt(r.volgnummer) || i;
    });

    // Find the next index.
    let nextIndex = 0;
    for (let i = 1; i <= relatedObject.length + 1; i++) {
      if (usedIndices.includes(i)) continue;
      nextIndex = i;
      break;
    }

    const relatedObjectStub = typedFields.reduce<RelatedObject<T>>(
      // @ts-expect-error - FIXME: Extending TypedField here.
      (acc, { name, type, initValue, options }) => {
        let value;

        if (initValue) {
          value = initValue();
        } else if (options) {
          value = options[0].value;
        } else {
          switch (type) {
            case "boolean":
              value = false;
              break;
            default:
              if (name === "omschrijvingGeneriek") {
                value = "behandelaar";
                break;
              }
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
      // @ts-expect-error - Loosely typed.
      relatedObjectStub["volgnummer"] = nextIndex;
    }

    submitAction({
      type: "ADD_RELATED_OBJECT",
      payload: {
        serviceSlug: serviceSlug,
        zaaktypeUuid: zaaktypeUuid,
        relatedObjectKey: field,
        relatedObject: relatedObjectStub,
      },
    });
  };

  /**
   * Handles editing an existing related object.
   *
   * @param relatedObject - The related object being updated
   */
  const handleEdit = (relatedObject: RelatedObject<T>) => {
    submitAction({
      type: "EDIT_RELATED_OBJECT",
      payload: {
        serviceSlug: serviceSlug,
        zaaktypeUuid: zaaktypeUuid,
        relatedObjectKey: field,
        relatedObject: relatedObject,
      },
    });
  };

  /**
   * Handles deleting a related object.
   *
   * @param relatedObject - The related object containing a `url` used for lookup
   */
  const handleDelete = (relatedObject: { url: string & RelatedObject<T> }) => {
    submitAction({
      type: "DELETE_RELATED_OBJECT",
      payload: {
        serviceSlug: serviceSlug,
        zaaktypeUuid: zaaktypeUuid,
        relatedObjectKey: field,
        relatedObjectUuid: getZaaktypeUUID(relatedObject) ?? "",
      },
    });
  };

  /**
   * A memoized list of related objects augmented with action buttons
   * (e.g., a delete button).
   */
  const augmentedObjectList = useMemo(
    () =>
      Array.isArray(relatedObject)
        ? relatedObject.map((row) => ({
            ...row,
            "": (
              <Button
                disabled={isLoading}
                size="xs"
                variant="danger"
                title="Verwijderen"
                onClick={() => handleDelete(row)}
              >
                <Outline.TrashIcon />
              </Button>
            ),
          }))
        : [],
    [relatedObject, isLoading],
  );

  if (!Array.isArray(relatedObject)) {
    if (!relatedObject) return null;

    return (
      <RelatedObjectBadge
        relatedObject={relatedObject}
        allowedFields={fieldNames}
      />
    );
  }

  if (view === "DataGrid") {
    return (
      <>
        <DataGrid<(typeof relatedObject)[number]>
          objectList={augmentedObjectList}
          fields={[
            // FIXME: Admin UI TypedField and our OBField should be compatible, but currently in admin-ui
            // filterValue is string | number, while for OBField it is unknown, since in the backend it is
            // a generic type based on the value of the object.
            // @ts-expect-error - see above
            ...typedFields,
            // @ts-expect-error - see above
            { name: "", type: "jsx", editable: false, sortable: false },
          ]}
          boolProps={{ explicit: true }}
          decorate
          editable={isEditing}
          editing={isEditing}
          sort="volgnummer"
          onEdit={(data) => {
            delete data[""]; // Action column.
            handleEdit(data as RelatedObject<T>);
          }}
          urlFields={[]}
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

  // Assume for attribute grid.
  return relatedObject.map((relatedObject, index) => (
    <RelatedObjectBadge
      key={typeof relatedObject.url === "string" ? relatedObject.url : index}
      relatedObject={relatedObject}
      allowedFields={expandFields}
    />
  ));
}

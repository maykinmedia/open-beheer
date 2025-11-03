import { FieldSet, TypedField, fields2TypedFields } from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import { useParams } from "react-router";
import { SERVICE_PARAM } from "~/App.tsx";
import {
  DEFAULT_ALLOWED_FIELDS,
  RelatedObjectBadge,
} from "~/components/related/RelatedObjectBadge.tsx";
import { TargetType } from "~/pages";
import { ExpandItemKeys, RelatedObject } from "~/types";

/**
 * Props for the {@link RelatedObjectRenderer} component.
 *
 * @typeParam T - The base object type for which related objects are expanded.
 */
type RelatedObjectRendererProps<
  T extends { url: string },
  R extends object = RelatedObject<T>,
> = {
  /** Array of all fields available for `object`. */
  fields: TypedField[];
  /** The parent object for which related objects are displayed. */
  object: T;
  /** Initial related object(s) to display. */
  relatedObject: RelatedObject<T>;
  /** Key in the parent object representing the relationship. */
  relatedObjectKey: ExpandItemKeys<T>;
  /** TODO: Replace with `fieldset`, The set of fields to expand and render. */
  expandFields?: TypedField[];
  /** FieldSet specifying which fields to include and their order. */
  fieldset?: FieldSet<R>;
};

/**
 * Renders either a DataGrid or a list of badges for a set of related objects,
 * depending on the tab configuration.
 */
export const RelatedObjectRenderer = <T extends TargetType>(
  props: RelatedObjectRendererProps<T>,
) => {
  const {
    expandFields: _expandFields,
    relatedObjectKey,
    fields,
    object,
    relatedObject,
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
    : fields
        .filter((f) => f.type === "string" || f.type === "text")
        .filter((f) => f.name !== "url")
        .filter((f) =>
          String(f.name).startsWith("_expand." + relatedObjectKey),
        );

  // This refers to the fields in an object which are allowed to be rendered for
  // a related object.
  //
  // To prevent unwanted results; DEFAULT_ALLOWED_FIELDS are always favored.
  // and other field names bound to the related object acts as fallback.
  const fallbackAllowedFields = expandFields.map((f) => f.name);

  const allowedFields = [
    ...DEFAULT_ALLOWED_FIELDS,
    ...fallbackAllowedFields,
  ] as unknown as keyof RelatedObject<T>;

  invariant("url" in object, "object should have url!");

  const params = useParams();
  const serviceSlug = params[SERVICE_PARAM];
  invariant(serviceSlug, "serviceSlug must be provided!");

  // Single related item in AttributeList.
  if (!Array.isArray(relatedObject)) {
    if (!relatedObject) return "-";

    return (
      <RelatedObjectBadge
        relatedObject={relatedObject}
        allowedFields={allowedFields}
      />
    );
  }

  // Multiple related items in AttributeList.
  if (Array.isArray(relatedObject)) {
    if (!relatedObject.length) {
      return "-";
    }

    return relatedObject.map((relatedObject, index) => (
      <RelatedObjectBadge
        key={relatedObject.uuid + index}
        relatedObject={relatedObject}
        allowedFields={allowedFields}
      />
    ));
  }
};
RelatedObjectRenderer.displayName = "RelatedObjectRenderer";

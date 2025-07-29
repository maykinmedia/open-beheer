import { DataGrid } from "@maykin-ui/admin-ui";
import { RelatedObjectBadge } from "~/components/related/RelatedObjectBadge.tsx";
import { ExpandItemKeys, Expanded } from "~/types";

type RelatedObjectRendererProps<T extends object> = {
  object: Expanded<T>;
  view: "AttributeGrid" | "DataGrid";
  expandFields: ExpandItemKeys<T>[];
  field: ExpandItemKeys<T>;
};

/**
 * Renders either a DataGrid or a list of badges for a set of related objects,
 * depending on the tab configuration.
 *
 * @param relatedObjects - The array of objects to render
 * @param view - The view type, either "DataGrid" or "AttributeGrid"
 * @param config - Tab configuration indicating view type and allowed fields
 */
export function RelatedObjectRenderer<T extends object>({
  object,
  view,
  expandFields,
  field,
}: RelatedObjectRendererProps<T>) {
  /**
   * Extracts an array of related objects from the expansion map.
   *
   * @param object - The object
   * @param field - The name of the field to extract from `expand`
   * @returns An array of related objects, or empty if none
   */
  const extractRelatedObjects = (
    object: Expanded<T>,
    field: keyof ExpandItemKeys<T>,
  ) => {
    const expand = object._expand;
    const value = expand?.[field as keyof typeof expand];

    if (!Array.isArray(value)) {
      console.error(
        `Expected an array for field "${field.toString()}" in _expand, but got:`,
        value,
      );
      return [];
    }
    return value;
  };

  const relatedObjects = extractRelatedObjects(object, field);
  if (!relatedObjects.length) return null;

  if (view !== "AttributeGrid") {
    return (
      <DataGrid<(typeof relatedObjects)[number]> // FIXME
        objectList={relatedObjects}
        urlFields={[]}
      />
    );
  }

  return (
    <>
      {relatedObjects.map((relatedObject, index) => (
        <RelatedObjectBadge<T>
          key={
            // @ts-expect-error - `url``not typed.
            typeof relatedObject.url === "string" ? relatedObject.url : index
          }
          relatedObject={relatedObject}
          allowedFields={expandFields}
        />
      ))}
    </>
  );
}

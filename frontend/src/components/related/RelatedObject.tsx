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
  const relatedObjects = object._expand?.[field];

  if (!Array.isArray(relatedObjects)) {
    if (!relatedObjects) return null;
    return (
      <RelatedObjectBadge
        relatedObject={relatedObjects}
        allowedFields={expandFields}
      />
    );
  }

  if (view === "DataGrid") {
    return (
      <DataGrid<(typeof relatedObjects)[number]>
        objectList={relatedObjects}
        urlFields={[]}
      />
    );
  }

  // Assume for attribute grid.
  return relatedObjects.map((relatedObject, index) => (
    <RelatedObjectBadge<T>
      key={typeof relatedObject.url === "string" ? relatedObject.url : index}
      relatedObject={relatedObject}
      allowedFields={expandFields}
    />
  ));
}

import { DataGrid } from "@maykin-ui/admin-ui";
import { RelatedObjectBadge } from "~/components/related/RelatedObjectBadge.tsx";
import { ExpandItemKeys } from "~/types";

type RelatedObjectRendererProps<T extends object> = {
  relatedObject: object | object[]; // TODO: Can improve typing
  view: "AttributeGrid" | "DataGrid";
  expandFields: ExpandItemKeys<T>[];
};

/**
 * Renders either a DataGrid or a list of badges for a set of related objects,
 * depending on the tab configuration.
 *
 * @param relatedObjects - The array of objects to render
 * @param view - The view type, either "DataGrid" or "AttributeGrid"
 */
export function RelatedObjectRenderer<T extends object>({
  relatedObject,
  view,
  expandFields,
}: RelatedObjectRendererProps<T>) {
  const _expandFields = ["transform", ...expandFields];
  if (!Array.isArray(relatedObject)) {
    if (!relatedObject) return null;

    return (
      <RelatedObjectBadge
        relatedObject={relatedObject}
        allowedFields={_expandFields}
      />
    );
  }

  if (view === "DataGrid") {
    return (
      <DataGrid<(typeof relatedObject)[number]>
        objectList={relatedObject}
        urlFields={[]}
      />
    );
  }

  // Assume for attribute grid.
  return relatedObject.map((relatedObject, index) => (
    <RelatedObjectBadge
      key={typeof relatedObject.url === "string" ? relatedObject.url : index}
      relatedObject={relatedObject}
      allowedFields={_expandFields}
    />
  ));
}

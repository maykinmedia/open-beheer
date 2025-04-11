import { DetailTemplate, FieldSet } from "@maykin-ui/admin-ui";
import { useLoaderData } from "react-router";

import "./Zaaktype.css";
import { ZaaktypeLoaderData } from "./zaaktype.loader.tsx";

/**
 * Zaaktype page
 */
export function ZaaktypePage() {
  const { demoData } = useLoaderData<ZaaktypeLoaderData>();

  const fieldsets: FieldSet<ZaaktypeLoaderData>[] = [
    [
      "Algemeen",
      {
        fields: ["id", "name", "age"],
        title: "name",
        span: 12,
      },
    ],
    [
      "Contact",
      {
        fields: ["email"],
        span: 12,
      },
    ],
  ];

  return (
    <DetailTemplate<ZaaktypeLoaderData>
      attributeGridProps={{
        fieldsets,
        object: demoData,
      }}
    />
  );
}

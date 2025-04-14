import { DetailTemplate, FieldSet } from "@maykin-ui/admin-ui";
import { useLoaderData } from "react-router";
import { ZaakType } from "~/pages";

/**
 * Zaaktype page
 */
export function ZaaktypePage<T extends { name: string } = ZaakType>() {
  const { data, fieldsets } = useLoaderData<{
    data: T;
    fieldsets: FieldSet<T>[];
  }>();

  return (
    <DetailTemplate<T>
      attributeGridProps={{
        title: data.name,
        fieldsets,
        object: data,
      }}
    />
  );
}

import { DetailTemplate } from "@maykin-ui/admin-ui";
import { useLoaderData } from "react-router";
import { ZaakType, ZaaktypeLoaderData } from "~/pages";

/**
 * Zaaktype page
 */
export function ZaaktypePage() {
  const { object, fieldsets } = useLoaderData<ZaaktypeLoaderData>();

  return (
    <DetailTemplate<ZaakType>
      attributeGridProps={{
        title: object.name,
        fieldsets,
        object: object,
      }}
    />
  );
}

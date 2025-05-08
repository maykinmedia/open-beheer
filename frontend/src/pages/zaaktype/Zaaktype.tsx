import { DetailTemplate } from "@maykin-ui/admin-ui";
import { useLoaderData } from "react-router";
import { useBreadcrumbItems } from "~/hooks";
import { ZaaktypeLoaderData } from "~/pages";
import { ZaakType } from "~/types";

/**
 * Zaaktype page
 */
export function ZaaktypePage() {
  const breadcrumbItems = useBreadcrumbItems();
  const { result, fieldsets } = useLoaderData<ZaaktypeLoaderData>();

  return (
    <DetailTemplate<ZaakType>
      breadcrumbItems={breadcrumbItems}
      attributeGridProps={{
        title: result.identificatie,
        fieldsets,
        object: result,
      }}
    />
  );
}

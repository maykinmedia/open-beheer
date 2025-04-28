import { DetailTemplate, Sidebar } from "@maykin-ui/admin-ui";
import { useLoaderData } from "react-router";
import { ZaaktypeLoaderData } from "~/pages";
import { ZaakType } from "~/types";

/**
 * Zaaktype page
 */
export function ZaaktypePage() {
  const { object, fieldsets } = useLoaderData<ZaaktypeLoaderData>();

  return (
    <DetailTemplate<ZaakType>
      cardProps={{
        direction: "row",
      }}
      attributeGridProps={{
        title: object.identificatie,
        fieldsets,
        object: object,
      }}
    >
      <Sidebar expandable={false} />
    </DetailTemplate>
  );
}

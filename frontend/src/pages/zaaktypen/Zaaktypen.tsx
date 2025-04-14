import { useLoaderData } from "react-router";
import { ZaaktypenLoaderData } from "~/pages";
import { ListView } from "~/views";

/**
 * Zaaktypen page
 */
export function ZaaktypenPage() {
  const { objectList, fieldsets } = useLoaderData<ZaaktypenLoaderData>();
  return (
    <ListView objectList={objectList} fieldsets={fieldsets} title="Zaaktypen" />
  );
}

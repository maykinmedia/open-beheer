import { useLoaderData } from "react-router";
import { ZaaktypenLoaderData } from "~/pages";
import { ListView } from "~/views";

/**
 * Zaaktypen page
 */
export function ZaaktypenPage() {
  const loaderData = useLoaderData<ZaaktypenLoaderData>();
  return <ListView {...loaderData} />;
}

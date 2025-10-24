import { request } from "~/api";
import { components } from "~/types";

export type ZaaktypeCreateLoaderData =
  components["schemas"]["ZGWResponse_Sjabloon_OptionalExpandableZaakTypeRequest_"];

/**
 * Zaaktypecreate loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypeCreatePage.
 */
export async function zaaktypeCreateLoader(): Promise<
  ZaaktypeCreateLoaderData | undefined
> {
  return await request<
    components["schemas"]["ZGWResponse_Sjabloon_OptionalExpandableZaakTypeRequest_"]
  >("GET", `/template/zaaktype/`);
}

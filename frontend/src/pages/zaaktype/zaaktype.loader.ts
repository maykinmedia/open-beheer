import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { components } from "~/types";

export type ZaaktypeLoaderData =
  components["schemas"]["DetailResponse_ExpandableZaakType_"];

/**
 * Zaaktype loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypePage.
 */
export async function zaaktypeLoader(
  loaderFunctionArgs: LoaderFunctionArgs,
): Promise<ZaaktypeLoaderData | undefined> {
  const { params } = loaderFunctionArgs;
  return await request<
    components["schemas"]["DetailResponse_ExpandableZaakType_"]
  >("GET", `/service/${params.serviceSlug}/zaaktypen/${params.zaaktypeUUID}/`);
}

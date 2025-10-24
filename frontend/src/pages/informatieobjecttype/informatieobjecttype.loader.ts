import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { components } from "~/types";

export type InformatieObjectTypeLoaderData =
  components["schemas"]["DetailResponseWithoutVersions_InformatieObjectType_"];

/**
 * Zaaktype loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypePage.
 */
export async function informatieobjecttypeLoader(
  loaderFunctionArgs: LoaderFunctionArgs,
): Promise<InformatieObjectTypeLoaderData | undefined> {
  const { params } = loaderFunctionArgs;
  return await request<
    components["schemas"]["DetailResponseWithoutVersions_InformatieObjectType_"]
  >(
    "GET",
    `/service/${params.serviceSlug}/informatieobjecttypen/${params.informatieobjecttypeUUID}/`,
  );
}

import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { ListResponse } from "~/api/types";
import { components } from "~/types";

export type ZaaktypenLoaderData = ListResponse<
  components["schemas"]["ZaakTypeSummary"]
>;

/**
 * Zaaktypen loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypenPage.
 */
export async function zaaktypenLoader(
  loaderFunctionArgs: LoaderFunctionArgs,
): Promise<ZaaktypenLoaderData | undefined> {
  const { params } = loaderFunctionArgs;

  const searchParams = new URL(loaderFunctionArgs.request.url).searchParams;
  return await request<ListResponse<components["schemas"]["ZaakTypeSummary"]>>(
    "GET",
    `/service/${params.serviceSlug}/zaaktypen/`,
    {
      catalogus: params.catalogusId,
      ...Object.fromEntries(searchParams),
    },
  );
}

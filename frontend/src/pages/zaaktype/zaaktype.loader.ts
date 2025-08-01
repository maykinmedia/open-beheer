import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { components } from "~/types";

export type ZaaktypeLoaderData =
  components["schemas"]["DetailResponse_ExpandableZaakType_"];

/**
 * Zaaktype loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypePage.
 */
export const zaaktypeLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<ZaaktypeLoaderData> => {
    const { params } = loaderFunctionArgs;
    return await request<
      components["schemas"]["DetailResponse_ExpandableZaakType_"]
    >(
      "GET",
      `/service/${params.serviceSlug}/zaaktypen/${params.zaaktypeUUID}/`,
    );
  },
);

import { LoaderFunctionArgs } from "react-router";
import { DetailResponse, request } from "~/api";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { components } from "~/types";

export type ZaaktypeLoaderData = DetailResponse<
  components["schemas"]["ZaakType"]
>;

/**
 * Zaaktype loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypePage.
 */
export const zaaktypeLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<ZaaktypeLoaderData> => {
    const { params } = loaderFunctionArgs;
    const response = await request<
      DetailResponse<components["schemas"]["ZaakType"]>
    >("GET", `/service/${params.serviceSlug}/zaaktypen/${params.zaaktypeUUID}`);
    console.log(response);
    return { ...response };
  },
);

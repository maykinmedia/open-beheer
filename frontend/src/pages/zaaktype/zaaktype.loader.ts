import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { DetailResponse } from "~/api/types";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { ZaakType } from "~/types";

export type ZaaktypeLoaderData = DetailResponse<ZaakType>;

/**
 * Zaaktype loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypePage.
 */
export const zaaktypeLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<ZaaktypeLoaderData> => {
    const { params } = loaderFunctionArgs;
    const response = await request<DetailResponse<ZaakType>>(
      "GET",
      `/service/${params.serviceSlug}/zaaktypen/${params.zaaktypeUUID}`,
    );
    return { ...response };
  },
);

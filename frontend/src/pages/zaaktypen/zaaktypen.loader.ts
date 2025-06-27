import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { ListResponse } from "~/api/types";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { ZaakType } from "~/types";

export type ZaaktypenLoaderData = ListResponse<ZaakType>;

/**
 * Zaaktypen loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypenPage.
 */
export const zaaktypenLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<ZaaktypenLoaderData> => {
    const { params } = loaderFunctionArgs;

    // Skip fetching if detail view is active.
    if (params.zaaktypeUUID) {
      return {
        fields: [],
        pagination: { count: 0, page: 1, pageSize: 0 },
        results: [],
      };
    }

    const searchParams = new URL(loaderFunctionArgs.request.url).searchParams;
    const response = await request<ListResponse<ZaakType>>(
      "GET",
      `/service/${params.serviceSlug}/zaaktypen/`,
      {
        catalogus: params.catalogusId,
        ...Object.fromEntries(searchParams),
      },
    );
    return { ...response };
  },
);

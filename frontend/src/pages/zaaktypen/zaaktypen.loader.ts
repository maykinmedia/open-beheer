import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { ListResponse } from "~/api/types";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { components } from "~/types";

export type ZaaktypenLoaderData = ListResponse<
  components["schemas"]["ZaakTypeSummary"]
>;

/**
 * Zaaktypen loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypenPage.
 */
export const zaaktypenLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<ZaaktypenLoaderData> => {
    const { params } = loaderFunctionArgs;

    const searchParams = new URL(loaderFunctionArgs.request.url).searchParams;
    const search = searchParams.get("search");
    searchParams.delete("search");

    const queryParams = new URLSearchParams(searchParams);
    if (search) {
      queryParams.set("identificatie__icontains", search);
    }

    const response = await request<
      ListResponse<components["schemas"]["ZaakTypeSummary"]>
    >("GET", `/service/${params.serviceSlug}/zaaktypen/`, queryParams);
    return { ...response };
  },
);

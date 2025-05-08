import { FieldSet } from "@maykin-ui/admin-ui";
import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { ListResponse } from "~/api/types";
import { ZAAKTYPE_FIELDSETS } from "~/fieldsets";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { ZaakType } from "~/types";

export type ZaaktypenLoaderData = ListResponse<ZaakType> & {
  fieldsets: FieldSet<ZaakType>[];
};

/**
 * Zaaktypen loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypenPage.
 */
export const zaaktypenLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<ZaaktypenLoaderData> => {
    const url = new URL(loaderFunctionArgs.request.url);
    const params = url.searchParams;
    const response = await request("GET", "/catalogi/zaaktypen", params);
    const listResponse: ListResponse<ZaakType> = await response.json();
    return { ...listResponse, fieldsets: ZAAKTYPE_FIELDSETS };
  },
);

import { FieldSet } from "@maykin-ui/admin-ui";
import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { DetailResponse } from "~/api/types";
import { ZAAKTYPE_FIELDSETS } from "~/fieldsets";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { ZaakType } from "~/types";

export type ZaaktypeLoaderData = DetailResponse<ZaakType> & {
  fieldsets: FieldSet<ZaakType>[];
};

/**
 * Zaaktype loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypePage.
 */
export const zaaktypeLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<ZaaktypeLoaderData> => {
    const url = new URL(loaderFunctionArgs.request.url);
    const uuid = loaderFunctionArgs.params.uuid;
    const params = url.searchParams;
    const response = await request(
      "GET",
      `/catalogi/zaaktypen/${uuid}`,
      params,
    );
    const detailReponse: DetailResponse<ZaakType> = await response.json();
    return { ...detailReponse, fieldsets: ZAAKTYPE_FIELDSETS };
  },
);

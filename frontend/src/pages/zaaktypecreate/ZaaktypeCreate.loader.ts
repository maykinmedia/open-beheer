import { request } from "~/api";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { components } from "~/types";

export type ZaaktypeCreateLoaderData = {
  count: number;
  next: string | null;
  previous: string | null;
  results: components["schemas"]["Sjabloon_OptionalZaakType_"][];
};

/**
 * Zaaktypecreate loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypeCreatePage.
 */
export const zaaktypeCreateLoader = loginRequired(
  async (): Promise<ZaaktypeCreateLoaderData> => {
    return await request<
      components["schemas"]["ZGWResponse_Sjabloon_OptionalZaakType_"]
    >("GET", `/template/zaaktype/`);
  },
);

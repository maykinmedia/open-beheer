import { request } from "~/api";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { components } from "~/types";

export type ZaaktypeCreateLoaderData =
  components["schemas"]["ZGWResponse_Sjabloon_OptionalExpandableZaakTypeRequest_"];

/**
 * Zaaktypecreate loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypeCreatePage.
 */
export const zaaktypeCreateLoader = loginRequired(
  async (): Promise<ZaaktypeCreateLoaderData> => {
    return await request<
      components["schemas"]["ZGWResponse_Sjabloon_OptionalExpandableZaakTypeRequest_"]
    >("GET", `/template/zaaktype/`);
  },
);

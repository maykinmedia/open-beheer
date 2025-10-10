import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { components } from "~/types";

export type InformatieObjectTypeLoaderData =
  components["schemas"]["DetailResponseWithoutVersions_InformatieObjectType_"];

/**
 * Zaaktype loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypePage.
 */
export const informatieobjecttypeLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<InformatieObjectTypeLoaderData> => {
    const { params } = loaderFunctionArgs;
    return await request<
      components["schemas"]["DetailResponseWithoutVersions_InformatieObjectType_"]
    >(
      "GET",
      `/service/${params.serviceSlug}/informatieobjecttypen/${params.informatieobjecttypeUUID}/`,
    );
  },
);

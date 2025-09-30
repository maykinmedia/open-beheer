import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { ListResponse } from "~/api/types";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { components } from "~/types";

export type InformatieObjectTypenLoaderData = ListResponse<
  components["schemas"]["InformatieObjectTypeSummary"]
>;

export const informatieobjecttypenLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<InformatieObjectTypenLoaderData> => {
    const { params } = loaderFunctionArgs;
    const searchParams = new URL(loaderFunctionArgs.request.url).searchParams;
    const response = await request<
      ListResponse<components["schemas"]["InformatieObjectTypeSummary"]>
    >("GET", `/service/${params.serviceSlug}/informatieobjecttypen/`, {
      catalogus: params.catalogusId,
      ...Object.fromEntries(searchParams),
    });
    return { ...response };
  },
);

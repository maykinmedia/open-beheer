import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";
import { components } from "~/types";
import { ListResponse } from "~/api/types";

export type InformatieObjectTypenLoaderData =  ListResponse<components["schemas"]["InformatieObjectTypeSummary"]>;

export const informatieobjecttypenLoader = loginRequired(
  async (
    loaderFunctionArgs: LoaderFunctionArgs,
  ): Promise<InformatieObjectTypenLoaderData> => {
    const { params } = loaderFunctionArgs;
    
        // Skip fetching if detail view is active.
        // if (params.informatieobjecttypeUUID) {
        //   return {
        //     fields: [],
        //     pagination: { count: 0, page: 1, pageSize: 0 },
        //     results: [],
        //   };
        // }
    
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
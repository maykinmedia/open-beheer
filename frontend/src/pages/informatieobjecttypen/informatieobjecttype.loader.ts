import { LoaderFunctionArgs } from "react-router";
import { request } from "~/api";
import { ListResponse } from "~/api/types";
import { components } from "~/types";

export type InformatieObjectTypenLoaderData = ListResponse<
  components["schemas"]["InformatieObjectTypeSummary"]
>;

export async function informatieobjecttypenLoader(
  loaderFunctionArgs: LoaderFunctionArgs,
): Promise<InformatieObjectTypenLoaderData | undefined> {
  const { params } = loaderFunctionArgs;
  const searchParams = new URL(loaderFunctionArgs.request.url).searchParams;
  return await request<
    ListResponse<components["schemas"]["InformatieObjectTypeSummary"]>
  >("GET", `/service/${params.serviceSlug}/informatieobjecttypen/`, {
    catalogus: params.catalogusId,
    ...Object.fromEntries(searchParams),
  });
}

import { ActionFunctionArgs, redirect } from "react-router";
import { request as _request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction.tsx";
import { components } from "~/types";

export type InformatieObjectTypeCreateAction = TypedAction<
  "INFORMATIEOBJECTTYPE_CREATE",
  InformatieObjectTypeCreateActionPayload
>;

export type InformatieObjectTypeCreateActionPayload =
  components["schemas"]["InformatieObjectTypeRequest"];

export async function informatieobjecttypeCreateAction({
  request,
  params,
}: ActionFunctionArgs): Promise<Response> {
  const data = await request.json();

  try {
    await _request<components["schemas"]["InformatieObjectType"]>(
      "POST",
      `/service/${params.serviceSlug}/informatieobjecttypen/`,
      {},
      data.payload,
    );
  } catch (e: unknown) {
    if (e instanceof Response) {
      return await e.json();
    }
    throw e;
  }

  // TODO: we will eventually redirect to the detail view, but that doesn't exist yet. For now redirect to list view.
  // const iotUrl = responseData.url!; // We know that Open Zaak always returns a URL
  // const nextPath = `/${params.serviceSlug}/${params.catalogusId}/informatieobjecttypen/${getUUIDFromString(iotUrl)}`;
  return redirect(
    `/${params.serviceSlug}/${params.catalogusId}/informatieobjecttypen/`,
  );
}

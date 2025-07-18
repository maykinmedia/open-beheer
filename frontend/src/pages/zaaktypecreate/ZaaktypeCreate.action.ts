import { ActionFunctionArgs, redirect } from "react-router";
import { request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction.ts";
import { PartialDeep, getZaaktypeUUID } from "~/lib";
import { ZaaktypeCreateLoaderData } from "~/pages";
import { components } from "~/types";

export type ZaakTypeCreateAction = TypedAction<
  "ZAAKTYPE_CREATE",
  ZaaktypeCreateActionPayload
>;
export type ZaaktypeCreateActionPayload = {
  zaaktype: PartialDeep<ZaaktypeCreateLoaderData["results"][0]>;
  serviceSlug: string;
  catalogusSlug: string;
};

/**
 * Zaaktypecreate action.
 * Action data can be obtained using `useActionData()` in ZaaktypeCreatePage.
 */
export async function zaaktypeCreateAction({
  request,
  params,
  context,
}: ActionFunctionArgs): Promise<
  ZaaktypeCreateActionPayload["zaaktype"] | Response
> {
  const data = await request.clone().json();
  const action = data as ZaakTypeCreateAction;

  switch (action.type) {
    case "ZAAKTYPE_CREATE":
      return await createZaaktypeAction({ request, params, context });
    default:
      throw new Error("INVALID ACTION TYPE SPECIFIED!");
  }
}

async function createZaaktypeAction(
  actionFunctionArgs: ActionFunctionArgs,
): Promise<ZaaktypeCreateActionPayload["zaaktype"] | Response> {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as ZaaktypeCreateActionPayload;

  try {
    const data = (await request(
      "POST",
      `/service/${payload.serviceSlug}/zaaktypen/`,
      {},
      { ...payload.zaaktype },
    )) as components["schemas"]["ZaakType"];
    const uuid = getZaaktypeUUID({ url: data.url });
    const nextPath = `/${payload.serviceSlug}/${payload.catalogusSlug}/zaaktypen/${uuid}`;
    return redirect(nextPath);
  } catch (e: unknown) {
    if (e instanceof Response) {
      return await e.json();
    }
    throw e;
  }
}

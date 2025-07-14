import { ActionFunctionArgs, redirect } from "react-router";
import { request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction.ts";
import { components } from "~/types";

export type ZaaktypeAction =
  | TypedAction<"CREATE_VERSION", CreateZaaktypeVersionPayload>
  | TypedAction<"SELECT_VERSION", SelectZaaktypeVersionPayload>;

/**
 * Zaaktype action.
 * Action data can be obtained using `useActionData()` in ZaaktypePage.
 */
export async function zaaktypeAction({
  request,
  params,
  context,
}: ActionFunctionArgs) {
  const data = await request.clone().json();
  const action = data as ZaaktypeAction;

  switch (action.type) {
    case "CREATE_VERSION":
      return await createZaaktypeVersionAction({ request, params, context });
    case "SELECT_VERSION":
      return await selectZaaktypeVersionAction({ request, params, context });
    default:
      throw new Error("INVALID ACTION TYPE SPECIFIED!");
  }
}

/**
 * Payload for `createZaaktypeVersionAction`
 */
export type CreateZaaktypeVersionPayload = {
  serviceSlug: string;
  zaaktype: components["schemas"]["ZaakType"];
};

/**
 * Creates a new zaaktype version.
 */
export async function createZaaktypeVersionAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as CreateZaaktypeVersionPayload;

  const invalidKeys: (keyof components["schemas"]["ExpandableZaakType"])[] = [
    "_expand",
  ];

  const zaaktype = Object.fromEntries(
    Object.entries(payload.zaaktype).filter(([k, v]) => {
      // @ts-expect-error - checking wider type against subset.
      return v !== null && !invalidKeys.includes(k);
    }),
  );
  console.log({ zaaktype, payload, bronCatalogus: zaaktype.bronCatalogus });
  await request(
    "POST",
    `/service/${payload.serviceSlug}/zaaktypen/`,
    {},
    { ...zaaktype },
  );
}

/**
 * Payload for `selectZaaktypeVersionAction`
 */
export type SelectZaaktypeVersionPayload = {
  uuid: string;
};

/**
 * Creates a new zaaktype version.
 */
export async function selectZaaktypeVersionAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as SelectZaaktypeVersionPayload;
  return redirect(`../${payload.uuid}`);
}

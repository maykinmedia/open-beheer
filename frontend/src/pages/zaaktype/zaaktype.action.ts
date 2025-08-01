import { ActionFunctionArgs, redirect } from "react-router";
import { request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction.ts";
import { getZaaktypeUUID } from "~/lib";
import { TargetType } from "~/pages";
import { components } from "~/types";

export type ZaaktypeAction =
  | TypedAction<"CREATE_VERSION", CreateZaaktypeVersionPayload>
  | TypedAction<"UPDATE_VERSION", UpdateZaaktypeVersionPayload>
  | TypedAction<"EDIT_VERSION", EditZaaktypeVersionPayload>
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
    case "UPDATE_VERSION":
      return await updateZaaktypeVersionAction({ request, params, context });
    case "EDIT_VERSION":
      return await editZaaktypeVersionAction({ request, params, context });
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
  zaaktype: TargetType;
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

  const result = await request<components["schemas"]["ZaakType"]>(
    "POST",
    `/service/${payload.serviceSlug}/zaaktypen/`,
    {},
    { ...zaaktype },
  );

  return redirect(`../${getZaaktypeUUID(result)}?editing=true`);
}

/**
 * Payload for `updateZaaktypeVersionAction`
 */
export type UpdateZaaktypeVersionPayload = {
  serviceSlug: string;
  zaaktype: Partial<TargetType> & { url: string };
};

/**
 * Updates a new zaaktype version.
 */
export async function updateZaaktypeVersionAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as UpdateZaaktypeVersionPayload;
  const uuid = getZaaktypeUUID(payload.zaaktype);

  const invalidKeys: (keyof components["schemas"]["ExpandableZaakType"])[] = [
    "_expand",
  ];

  const zaaktype = Object.fromEntries(
    Object.entries(payload.zaaktype).filter(([k, v]) => {
      // @ts-expect-error - checking wider type against subset.
      return v !== null && !invalidKeys.includes(k);
    }),
  );

  await request(
    "PATCH",
    `/service/${payload.serviceSlug}/zaaktypen/${uuid}/`,
    {},
    { ...zaaktype },
  );

  return redirect(`../${uuid}`);
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

/**
 * Payload for `editZaaktypeVersionAction`
 */
export type EditZaaktypeVersionPayload = {
  uuid: string;
};

/**
 * Creates a new zaaktype version.
 */
export async function editZaaktypeVersionAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as EditZaaktypeVersionPayload;
  return redirect(`../${payload.uuid}?editing=true`);
}

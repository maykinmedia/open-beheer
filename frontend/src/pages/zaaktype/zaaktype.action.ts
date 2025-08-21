import { ActionFunctionArgs, redirect } from "react-router";
import { request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction.tsx";
import { getZaaktypeUUID } from "~/lib";
import { TargetType } from "~/pages";
import { components } from "~/types";

export type ZaaktypeAction =
  | TypedAction<"CREATE_VERSION", CreateZaaktypeVersionPayload>
  | TypedAction<"UPDATE_VERSION", PublishZaaktypeVersionPayload>
  | TypedAction<"PUBLISH_VERSION", UpdateZaaktypeVersionPayload>
  | TypedAction<"EDIT_VERSION", EditZaaktypeVersionPayload>
  | TypedAction<"EDIT_CANCEL", EditCancelZaaktypeVersionPayload>
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
    case "PUBLISH_VERSION":
      return await publishZaaktypeVersionAction({ request, params, context });
    case "EDIT_VERSION":
      return await editZaaktypeVersionAction({ request, params, context });
    case "EDIT_CANCEL":
      return await editCancelZaaktypeVersionAction({
        request,
        params,
        context,
      });
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

  try {
    const result = await request<components["schemas"]["ExpandableZaakType"]>(
      "POST",
      `/service/${payload.serviceSlug}/zaaktypen/`,
      {},
      { ...zaaktype },
    );
    return redirect(`../${getZaaktypeUUID(result)}?editing=true`);
  } catch (e) {
    return await (e as Response).json();
  }
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
  const payload = data.payload as PublishZaaktypeVersionPayload;
  const uuid = getZaaktypeUUID(payload.zaaktype);

  try {
    await _saveZaaktypeVersion(payload.zaaktype, payload.serviceSlug);
    return redirect(`../${uuid}`);
  } catch (e) {
    return await (e as Response).json();
  }
}

/**
 * Payload for `publishZaaktypeVersionAction`
 */
export type PublishZaaktypeVersionPayload = {
  serviceSlug: string;
  zaaktype: Partial<TargetType> & { url: string };
};

/**
 * Saves and publishes a zaaktype version.
 */
export async function publishZaaktypeVersionAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as PublishZaaktypeVersionPayload;
  const uuid = getZaaktypeUUID(payload.zaaktype);

  await _saveZaaktypeVersion(payload.zaaktype, payload.serviceSlug);

  try {
    await request(
      "POST",
      `/service/${payload.serviceSlug}/zaaktypen/${uuid}/publish`,
    );
    return redirect(`../${uuid}`);
  } catch (e) {
    return await (e as Response).json();
  }
}

async function _saveZaaktypeVersion(
  zaaktype: Partial<TargetType> & { url: string },
  serviceSlug: string,
) {
  const uuid = getZaaktypeUUID(zaaktype);

  const invalidKeys: (keyof components["schemas"]["ExpandableZaakType"])[] = [
    "_expand",
  ];

  const _zaaktype = Object.fromEntries(
    Object.entries(zaaktype).filter(([k, v]) => {
      // @ts-expect-error - checking wider type against subset.
      return v !== null && !invalidKeys.includes(k);
    }),
  );

  await request(
    "PATCH",
    `/service/${serviceSlug}/zaaktypen/${uuid}/`,
    {},
    { ..._zaaktype },
  );
}

/**
 * Payload for `selectZaaktypeVersionAction`
 */
export type SelectZaaktypeVersionPayload = {
  uuid: string;
};

/**
 * Navigates to a zaaktype version.
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
 * Allow the user to edit a zaaktype version.
 */
export async function editZaaktypeVersionAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as EditZaaktypeVersionPayload;
  return redirect(`../${payload.uuid}?editing=true`);
}

/**
 * Payload for `editCancelZaaktypeVersionAction`
 */
export type EditCancelZaaktypeVersionPayload = {
  uuid: string;
};

/**
 * Allow the user to cancel editting a zaaktype version.
 */
export async function editCancelZaaktypeVersionAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as EditZaaktypeVersionPayload;
  return redirect(`../${payload.uuid}`);
}

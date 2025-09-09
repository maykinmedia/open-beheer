import { ActionFunctionArgs, redirect } from "react-router";
import { request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction.tsx";
import { getZaaktypeUUID } from "~/lib";
import { TargetType, ZaaktypeLoaderData } from "~/pages";
import { RelatedObject, components } from "~/types";

export type ZaaktypeAction =
  | TypedAction<"CREATE_VERSION", CreateZaaktypeVersionPayload>
  | TypedAction<"UPDATE_VERSION", PublishZaaktypeVersionPayload>
  | TypedAction<"SAVE_AS", SaveAsZaaktypePayload>
  | TypedAction<"PUBLISH_VERSION", UpdateZaaktypeVersionPayload>
  | TypedAction<"EDIT_VERSION", EditZaaktypeVersionPayload>
  | TypedAction<"EDIT_CANCEL", EditCancelZaaktypeVersionPayload>
  | TypedAction<"SELECT_VERSION", SelectZaaktypeVersionPayload>
  | TypedAction<"EDIT_RELATED_OBJECT", EditRelatedObjectPayload>
  | TypedAction<"ADD_RELATED_OBJECT", AddRelatedObjectPayload>
  | TypedAction<"DELETE_RELATED_OBJECT", DeleteRelatedObjectPayload>;

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
    case "SAVE_AS":
      return await saveAsAction({ request, params, context });
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
    case "EDIT_RELATED_OBJECT":
      return await editRelatedObjectAction({ request, params, context });
    case "ADD_RELATED_OBJECT":
      return await addRelatedObjectAction({ request, params, context });
    case "DELETE_RELATED_OBJECT":
      return await deleteRelatedObjectAction({ request, params, context });
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
  const zaaktype = payload.zaaktype;

  try {
    const result = await request<components["schemas"]["ExpandableZaakType"]>(
      "POST",
      `/service/${payload.serviceSlug}/zaaktypen/`,
      {},
      zaaktype,
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
 * Payload for `updateZaaktypeVersionAction`
 */
export type SaveAsZaaktypePayload = {
  serviceSlug: string;
  zaaktype: Partial<TargetType> & { url: string };
};

/**
 * Updates a new zaaktype version.
 */
export async function saveAsAction(actionFunctionArgs: ActionFunctionArgs) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as PublishZaaktypeVersionPayload;
  const uuid = getZaaktypeUUID(payload.zaaktype);

  const zaaktype = payload.zaaktype;
  delete zaaktype.broncatalogus;
  delete zaaktype.bronzaaktype;

  try {
    await _saveZaaktypeVersion(zaaktype as TargetType, payload.serviceSlug);
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

  await request(
    "PATCH",
    `/service/${serviceSlug}/zaaktypen/${uuid}/`,
    {},
    zaaktype,
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

export type AddRelatedObjectPayload = {
  serviceSlug: string;
  zaaktypeUuid: string;

  relatedObjectKey: keyof ZaaktypeLoaderData["result"]["_expand"];
  relatedObject: RelatedObject<TargetType>;
};

/**
 * Action to add a related object.
 */
export async function addRelatedObjectAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as AddRelatedObjectPayload;

  try {
    await request(
      "POST",
      `/service/${payload.serviceSlug}/zaaktypen/${payload.zaaktypeUuid}/${payload.relatedObjectKey}/`,
      {},
      payload.relatedObject,
    );
  } catch (e: unknown) {
    return await (e as Response).json();
  }
}

export type EditRelatedObjectPayload = {
  serviceSlug: string;
  zaaktypeUuid: string;

  relatedObjectKey: keyof ZaaktypeLoaderData["result"]["_expand"];
  relatedObject: RelatedObject<TargetType>;
};

/**
 * Action to edit a related object.
 */
export async function editRelatedObjectAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as EditRelatedObjectPayload;
  const relatedObjectUuid = getZaaktypeUUID(payload.relatedObject);

  try {
    await request(
      "PUT",
      `/service/${payload.serviceSlug}/zaaktypen/${payload.zaaktypeUuid}/${payload.relatedObjectKey}/${relatedObjectUuid}`,
      {},
      payload.relatedObject,
    );
  } catch (e: unknown) {
    return await (e as Response).json();
  }
}

export type DeleteRelatedObjectPayload = {
  serviceSlug: string;
  zaaktypeUuid: string;

  relatedObjectKey: keyof ZaaktypeLoaderData["result"]["_expand"];
  relatedObjectUuid: string;
};

/**
 * Action to delete a related object.
 */
export async function deleteRelatedObjectAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as DeleteRelatedObjectPayload;

  try {
    return await request(
      "DELETE",
      `/service/${payload.serviceSlug}/zaaktypen/${payload.zaaktypeUuid}/${payload.relatedObjectKey}/${payload.relatedObjectUuid}`,
    );
  } catch (e: unknown) {
    return await (e as Response).json();
  }
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

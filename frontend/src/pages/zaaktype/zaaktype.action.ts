import { ActionFunctionArgs, redirect } from "react-router";
import { request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction.ts";
import { getObjectUUID } from "~/lib";
import { ZaaktypeLoaderData } from "~/pages";
import { RelatedObject, components } from "~/types";

export type ZaaktypeAction =
  | TypedAction<"CREATE_VERSION", CreateZaaktypeVersionPayload>
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

export type AddRelatedObjectPayload = {
  serviceSlug: string;
  zaaktypeUuid: string;

  relatedObjectKey: keyof ZaaktypeLoaderData["result"]["_expand"];
  relatedObject: RelatedObject<ZaaktypeLoaderData["result"]>;
};

/**
 * Action to add a related object.
 */
export async function addRelatedObjectAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as AddRelatedObjectPayload;

  console.log(`Adding related object: ${payload.relatedObjectKey}`);
  try {
    return await request(
      "POST",
      `/service/${payload.serviceSlug}/zaaktype/${payload.zaaktypeUuid}/${payload.relatedObjectKey}`,
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
  relatedObject: Partial<RelatedObject<ZaaktypeLoaderData["result"]>>;
};

/**
 * Action to edit a related object.
 */
export async function editRelatedObjectAction(
  actionFunctionArgs: ActionFunctionArgs,
) {
  const data = await actionFunctionArgs.request.json();
  const payload = data.payload as EditRelatedObjectPayload;

  console.log("Editing related object:", payload.relatedObject);

  if (!payload.relatedObject.url) {
    throw new Error("Related object must have a URL to edit it.");
  }
  const relatedObjectUuid = getObjectUUID(payload.relatedObject);

  try {
    return await request(
      "PATCH",
      `/service/${payload.serviceSlug}/zaaktype/${payload.zaaktypeUuid}/${payload.relatedObjectKey}/${relatedObjectUuid}`,
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

  console.log("Deleting related object:", payload.relatedObjectKey);

  try {
    return await request(
      "DELETE",
      `/service/${payload.serviceSlug}/zaaktype/${payload.zaaktypeUuid}/${payload.relatedObjectKey}/${payload.relatedObjectUuid}`,
    );
  } catch (e: unknown) {
    return await (e as Response).json();
  }
}

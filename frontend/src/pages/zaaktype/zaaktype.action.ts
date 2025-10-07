import { invariant } from "@maykin-ui/client-common/assert";
import { ActionFunctionArgs, redirect } from "react-router";
import { request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction.tsx";
import { dateToIsoDateString, getZaaktypeUUID, today, yesterday } from "~/lib";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { findActiveZaaktypeVersion } from "~/lib/zaaktype";
import { TargetType, ZaaktypeLoaderData } from "~/pages";
import { RelatedObject, components } from "~/types";

export type ZaaktypeAction =
  | TypedAction<"BATCH", BatchActionPayload>
  | TypedAction<"CREATE_VERSION", CreateZaaktypeVersionPayload>
  | TypedAction<"UPDATE_VERSION", UpdateZaaktypeVersionPayload>
  | TypedAction<"SAVE_AS", SaveAsZaaktypePayload>
  | TypedAction<"PUBLISH_VERSION", PublishZaaktypeVersionPayload>
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
export async function zaaktypeAction({ request }: ActionFunctionArgs) {
  const data = await request.clone().json();
  const action = data as ZaaktypeAction;
  return await performAction(action);
}

export async function performAction(action: ZaaktypeAction): Promise<unknown> {
  switch (action.type) {
    case "BATCH":
      return await batchAction(action);

    case "CREATE_VERSION":
      return await createZaaktypeVersionAction(action);
    case "UPDATE_VERSION":
      return await updateZaaktypeVersionAction(action);
    case "SAVE_AS":
      return await saveAsAction(action);
    case "PUBLISH_VERSION":
      return await publishZaaktypeVersionAction(action);
    case "EDIT_VERSION":
      return await editZaaktypeVersionAction(action);
    case "EDIT_CANCEL":
      return await editCancelZaaktypeVersionAction(action);
    case "SELECT_VERSION":
      return await selectZaaktypeVersionAction(action);
    case "EDIT_RELATED_OBJECT":
      return await editRelatedObjectAction(action);
    case "ADD_RELATED_OBJECT":
      return await addRelatedObjectAction(action);
    case "DELETE_RELATED_OBJECT":
      return await deleteRelatedObjectAction(action);
    default:
      throw new Error("INVALID ACTION TYPE SPECIFIED!");
  }
}

/**
 * Payload for `batchAction`
 */
export type BatchActionPayload = {
  zaaktype: Partial<TargetType>;
  actions: ZaaktypeAction[];
};

/**
 * Runs multiple actions.
 */
export async function batchAction(
  action: TypedAction<"BATCH", BatchActionPayload>,
) {
  const payload = action.payload;
  const zaaktype = payload.zaaktype;
  const uuid = getUUIDFromString(zaaktype.uuid || zaaktype.url || "");
  invariant(uuid, "either zaaktype.uuid or zaaktype.url must be set");

  const actions = payload.actions;
  const promises = actions.map((action) => performAction(action));

  try {
    const result = await Promise.all<object>(promises);
    const errors = result.filter(
      (r: object) =>
        r && "status" in r && typeof r.status === "number" && r.status >= 400,
    );
    if (errors?.length) {
      return errors;
    }

    const url = new URL(window.location.href);
    url.searchParams.delete("editing");
    return redirect(url.toString());
  } catch (e) {
    return e;
  }
}

/**
 * Payload for `createZaaktypeVersionAction`
 */
export type CreateZaaktypeVersionPayload = {
  serviceSlug: string;
  zaaktype: Partial<TargetType>;
};

/**
 * Creates a new zaaktype version.
 */
export async function createZaaktypeVersionAction(
  action: TypedAction<"CREATE_VERSION", CreateZaaktypeVersionPayload>,
) {
  const payload = action.payload;
  const zaaktype = payload.zaaktype;
  delete zaaktype.broncatalogus;
  delete zaaktype.bronzaaktype;

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
  zaaktype: Partial<TargetType>;
};

/**
 * Updates a new zaaktype version.
 */
export async function updateZaaktypeVersionAction(
  action: TypedAction<"UPDATE_VERSION", UpdateZaaktypeVersionPayload>,
) {
  const payload = action.payload;
  const zaaktype = payload.zaaktype;
  const uuid = getUUIDFromString(zaaktype.uuid || zaaktype.url || "");
  invariant(uuid, "either zaaktype.uuid or zaaktype.url must be set");

  try {
    await _saveZaaktypeVersion(payload.zaaktype, payload.serviceSlug);

    const url = new URL(window.location.href);
    url.searchParams.delete("editing");
    return redirect(url.toString());
  } catch (e) {
    return await (e as Response).json();
  }
}

/**
 * Payload for `updateZaaktypeVersionAction`
 */
export type SaveAsZaaktypePayload = {
  serviceSlug: string;
  zaaktype: Partial<TargetType>;
};

/**
 * Updates a new zaaktype version.
 */
export async function saveAsAction(
  action: TypedAction<"SAVE_AS", SaveAsZaaktypePayload>,
) {
  const payload = action.payload;
  const serviceSlug = payload.serviceSlug;
  const zaaktype = payload.zaaktype;
  delete zaaktype.broncatalogus;
  delete zaaktype.bronzaaktype;

  // 1/2 - Filter these fields from related objects in `_expand`
  const expandFieldBlackList = ["url", "uuid"];

  // 2/2 - Unless the related object's key is one of
  const expandObjectWhitelist = [
    "besluittypen",
    "informatieobjecttypen",
    "selectielijstProcestype",
  ];

  // Perform filtering as describe above.
  for (const _key in zaaktype._expand) {
    const key = _key as keyof typeof zaaktype._expand;
    const value = zaaktype._expand[key];

    // Don't filter if key is in expandObjectWhitelist
    if (expandObjectWhitelist.includes(_key.toLowerCase())) {
      continue;
    }

    // Handler, can be used with Array item or direct value
    const handle = <T>(obj: T) => {
      if (!obj) return obj;
      return Object.fromEntries(
        Object.entries(obj).filter(([k]) => !expandFieldBlackList.includes(k)),
      );
    };

    // Reassign filtered value
    // @ts-expect-error - Dropping keys here.
    zaaktype._expand[key] = Array.isArray(value)
      ? value.map(handle)
      : handle(value);
  }

  try {
    const { uuid } = await request<components["schemas"]["ZaakTypeWithUUID"]>(
      "POST",
      `/service/${serviceSlug}/zaaktypen/`,
      {},
      zaaktype,
    );
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
  zaaktype: Partial<TargetType>;
  versions: components["schemas"]["VersionSummary"][];
};

/**
 * Saves and publishes a zaaktype version.
 */
export async function publishZaaktypeVersionAction(
  action: TypedAction<"PUBLISH_VERSION", PublishZaaktypeVersionPayload>,
) {
  const payload = action.payload;
  const zaaktype = payload.zaaktype;
  const uuid = getUUIDFromString(zaaktype.uuid || zaaktype.url || "");
  invariant(uuid, "either zaaktype.uuid or zaaktype.url must be set");

  const versions = payload.versions;
  const activeVersion = findActiveZaaktypeVersion(versions);

  await _saveZaaktypeVersion(payload.zaaktype, payload.serviceSlug);

  try {
    // Unpublish current version (if any)
    if (activeVersion) {
      await request(
        "PATCH",
        `/service/${payload.serviceSlug}/zaaktypen/${activeVersion.uuid}/`,
        undefined,
        {
          eindeGeldigheid: dateToIsoDateString(yesterday()),
        },
      );
    }

    // Set beginGeldigheid to today (if not set or clashes with previously published version)
    if (
      !zaaktype.beginGeldigheid ||
      (zaaktype.beginGeldigheid &&
        new Date(zaaktype.beginGeldigheid) <= today())
    ) {
      await request(
        "PATCH",
        `/service/${payload.serviceSlug}/zaaktypen/${uuid}/`,
        undefined,
        {
          beginGeldigheid: dateToIsoDateString(today()),
        },
      );
    }

    // Publish new version.
    await request(
      "POST",
      `/service/${payload.serviceSlug}/zaaktypen/${uuid}/publish`,
    );
  } catch (e) {
    return await (e as Response).json();
  }
}

async function _saveZaaktypeVersion(
  zaaktype: Partial<TargetType>,
  serviceSlug: string,
) {
  const uuid = getUUIDFromString(zaaktype.uuid || zaaktype.url || "");
  invariant(uuid, "either zaaktype.uuid or zaaktype.url must be set");

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
  action: TypedAction<"SELECT_VERSION", SelectZaaktypeVersionPayload>,
) {
  const payload = action.payload;

  const url = new URL(window.location.href);
  url.searchParams.delete("editing");
  return redirect(`../${payload.uuid}${url.search}${url.hash}`);
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
  action: TypedAction<"EDIT_VERSION", EditZaaktypeVersionPayload>,
) {
  const payload = action.payload;

  const url = new URL(window.location.href);
  url.searchParams.set("editing", "true");
  return redirect(`../${payload.uuid}${url.search}${url.hash}`);
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
  action: TypedAction<"ADD_RELATED_OBJECT", AddRelatedObjectPayload>,
) {
  const payload = action.payload;

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
  action: TypedAction<"EDIT_RELATED_OBJECT", EditRelatedObjectPayload>,
) {
  const payload = action.payload;
  const relatedObject = payload.relatedObject;
  const relatedObjectUuid = getUUIDFromString(
    relatedObject.uuid || relatedObject.url || "",
  );
  invariant(
    relatedObjectUuid,
    "either relatedObject.uuid or relatedObject.url must be set",
  );

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
  action: TypedAction<"DELETE_RELATED_OBJECT", DeleteRelatedObjectPayload>,
) {
  const payload = action.payload;

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
 * Allow the user to cancel editing a zaaktype version.
 */
export async function editCancelZaaktypeVersionAction(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _action: TypedAction<"EDIT_CANCEL", EditCancelZaaktypeVersionPayload>,
) {
  const url = new URL(window.location.href);
  url.searchParams.delete("editing");
  return redirect(url.toString());
}

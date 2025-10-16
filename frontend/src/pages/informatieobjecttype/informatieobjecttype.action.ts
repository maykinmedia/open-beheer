import { ActionFunctionArgs, Params, redirect } from "react-router";
import { request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction";
import { components } from "~/types";

export type BackendIOT = components["schemas"]["InformatieObjectType"];
export type PatchedBackendIOT =
  components["schemas"]["PatchedPatchedInformatieObjectTypeRequest"];

export type InformatieObjectTypeAction =
  | TypedAction<"UPDATE", PatchedBackendIOT>
  | TypedAction<"UPDATE_AND_PUBLISH", PatchedBackendIOT>
  | TypedAction<"SET_EDIT_MODE_ON">
  | TypedAction<"SET_EDIT_MODE_OFF">
  | TypedAction<"PUBLISH">;

export async function informatieobjecttypeAction({
  request,
  params,
}: ActionFunctionArgs) {
  const action = await request.clone().json();

  switch (action.type) {
    case "UPDATE":
      return await updateInformatieObjectTypeVersion(action, params);
    case "PUBLISH":
      return await publishInformatieObjectTypeVersion(params);
    case "UPDATE_AND_PUBLISH":
      return await updateAndPublishInformatieObjectTypeVersion(action, params);
    case "SET_EDIT_MODE_ON":
      return await setEditModeOn();
    case "SET_EDIT_MODE_OFF":
      return await setEditModeOff();
    default:
      throw new Error("INVALID ACTION TYPE SPECIFIED!");
  }
}

export async function updateInformatieObjectTypeVersion(
  action: InformatieObjectTypeAction,
  params: Params,
): Promise<Response> {
  const informatieobjecttype = action.payload as PatchedBackendIOT;

  if (informatieobjecttype) {
    try {
      await request<PatchedBackendIOT>(
        "PATCH",
        `/service/${params.serviceSlug}/informatieobjecttypen/${params.informatieobjecttypeUUID}/`,
        {},
        informatieobjecttype,
      );
    } catch (e) {
      return await (e as Response).json();
    }
  }

  const url = new URL(window.location.href);
  url.searchParams.delete("editing");
  return redirect(url.toString());
}

export async function updateAndPublishInformatieObjectTypeVersion(
  action: InformatieObjectTypeAction,
  params: Params,
): Promise<Response> {
  const informatieobjecttype = action.payload as PatchedBackendIOT;

  try {
    await request(
      "PATCH",
      `/service/${params.serviceSlug}/informatieobjecttypen/${params.informatieobjecttypeUUID}/`,
      {},
      informatieobjecttype,
    );
    await request(
      "POST",
      `/service/${params.serviceSlug}/informatieobjecttypen/${params.informatieobjecttypeUUID}/publish/`,
      {},
    );
  } catch (e) {
    return await (e as Response).json();
  }

  const url = new URL(window.location.href);
  url.searchParams.delete("editing");
  return redirect(url.toString());
}

export async function publishInformatieObjectTypeVersion(params: Params) {
  try {
    await request(
      "POST",
      `/service/${params.serviceSlug}/informatieobjecttypen/${params.informatieobjecttypeUUID}/publish/`,
      {},
    );
  } catch (e) {
    return await (e as Response).json();
  }

  const url = new URL(window.location.href);
  url.searchParams.delete("editing");
  return redirect(url.toString());
}

export async function setEditModeOn(): Promise<Response> {
  const url = new URL(window.location.href);
  url.searchParams.set("editing", "true");
  return redirect(url.href);
}

export async function setEditModeOff(): Promise<Response> {
  const url = new URL(window.location.href);
  url.searchParams.delete("editing");
  return redirect(url.href);
}

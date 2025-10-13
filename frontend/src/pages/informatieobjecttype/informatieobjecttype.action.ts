import { ActionFunctionArgs, Params, redirect } from "react-router";
import { request } from "~/api";
import { TypedAction } from "~/hooks/useSubmitAction";
import { components } from "~/types";

export type BackendIOT = components["schemas"]["InformatieObjectType"];

export type InformatieObjectTypeAction =
  | TypedAction<"UPDATE", Partial<BackendIOT>>
  | TypedAction<"SET_EDIT_MODE_ON">
  | TypedAction<"SET_EDIT_MODE_OFF">;

export async function informatieobjecttypeAction({
  request,
  params,
}: ActionFunctionArgs) {
  const action = await request.clone().json();

  switch (action.type) {
    case "UPDATE":
      return await updateInformatieObjectTypeVersion(action, params);
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
  const informatieobjecttype = action.payload;

  try {
    await request(
      "PATCH",
      `/service/${params.serviceSlug}/informatieobjecttypen/${params.informatieobjecttypeUUID}/`,
      {},
      informatieobjecttype,
    );

    const url = new URL(window.location.href);
    url.searchParams.delete("editing");
    return redirect(url.toString());
  } catch (e) {
    return await (e as Response).json();
  }
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

import { ActionFunctionArgs } from "react-router";

import "./Login.css";

export type LoginActionData = object;

/**
 * Login action.
 * Action data can be obtained using `useActionData()` in LoginPage.
 */
export async function loginAction({
  request,
}: ActionFunctionArgs): Promise<LoginActionData> {
  const formData = await request.formData();
  const username = formData.get("username");
  const password = formData.get("password");

  console.log("Login action", { username, password });
  return {
    nonFieldErrors: ["Login not implemented yet"],
  };
}

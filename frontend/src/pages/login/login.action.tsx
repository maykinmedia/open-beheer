import { ActionFunctionArgs, redirect } from "react-router";
import { login } from "~/lib/api/auth.ts";

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
  const loginAbortController = new AbortController();

  try {
    await login(
      username as string,
      password as string,
      loginAbortController.signal,
    );
    const url = new URL(request.url);
    const next = url.searchParams.get("next") || "/";
    const nextPath = new URL(next, window.location.origin).pathname;

    return redirect(nextPath);
  } catch (e: unknown) {
    return await (e as Response).json();
  }
}

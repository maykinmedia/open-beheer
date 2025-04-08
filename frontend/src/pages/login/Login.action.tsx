import "./Login.css";

export type LoginActionData = object;

/**
 * Login action.
 * Action data can be obtained using `useActionData()` in LoginPage.
 */
export async function loginAction(): Promise<LoginActionData> {
  // const formData = await request.formData();
  // const username = formData.get("username");
  // const password = formData.get("password");

  return {
    nonFieldErrors: ["Login not implemented yet"],
  };
}

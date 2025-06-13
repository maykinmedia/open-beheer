import { request } from "~/api/request.ts";

export type User = {
  pk: number;
  username: string;
  firstName: string;
  lastName: string;
  email: string;
};

/**
 * API call for login.
 * @param username - username of the user
 * @param password - password of the user
 * @param signal - optional abort signal to cancel the request
 */
export async function login(
  username: string,
  password: string,
  signal?: AbortSignal,
) {
  return request<void>(
    "POST",
    "/auth/login/",
    undefined,
    {
      username,
      password,
    },
    undefined,
    signal,
  );
}

/**
 * API call to get the current logged-in user.
 */
export async function whoAmI(signal?: AbortSignal) {
  return await request<User>(
    "GET",
    "/whoami/",
    undefined,
    undefined,
    undefined,
    signal,
  );
}

/**
 * API call for logout.
 */
export async function logout(signal?: AbortSignal) {
  return request<void>(
    "POST",
    "/auth/logout/",
    undefined,
    undefined,
    undefined,
    signal,
  );
}

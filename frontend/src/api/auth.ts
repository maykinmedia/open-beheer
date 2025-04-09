import { request } from "~/api/request.ts";

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
  return request(
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
 * API call for logout.
 */
export async function logout(signal?: AbortSignal) {
  return request(
    "POST",
    "/auth/logout/",
    undefined,
    undefined,
    undefined,
    signal,
  );
}

import { cacheDelete, cacheMemo } from "@maykin-ui/client-common";
import { request } from "~/api/request.ts";
import { components } from "~/types";

import { OidcInfoType } from "./types";

export function ensureCSRF() {
  return request("GET", "/auth/ensure-csrf/");
}

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

/** Cache key used for storing and removing cache during login/logout. */
const CACHE_KEY_WHOAMI = "whoAmI";

/**
 * API call to get the current logged-in user.
 */
export async function whoAmI(signal?: AbortSignal) {
  return cacheMemo(CACHE_KEY_WHOAMI, request<components["schemas"]["User"]>, [
    "GET",
    "/whoami/",
    undefined,
    undefined,
    undefined,
    signal,
  ]);
}

/**
 * API call for logout.
 */
export async function logout(signal?: AbortSignal) {
  await cacheDelete(CACHE_KEY_WHOAMI);
  return request<void>(
    "POST",
    "/auth/logout/",
    undefined,
    undefined,
    undefined,
    signal,
  );
}

/**
 * API call to get info about OIDC.
 */
export async function getOIDCInfo() {
  return request<OidcInfoType>("GET", "/oidc-info/");
}

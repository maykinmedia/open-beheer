import { getCookie } from "@maykin-ui/client-common/cookie";

/** The base origin for all API requests. */
export const API_URL = import.meta.env.MYKN_API_URL || window.location.origin;

/** The base path for all API requests. */
export const API_PATH = import.meta.env.MYKN_API_PATH || "/api/v1";

/** The base url for all API requests. */
export const API_BASE_URL = `${API_URL}${API_PATH}`;

/**
 * Makes an actual fetch request to the API, should be used by all other API implementations.
 * @param method - method to use for the request
 * @param endpoint - the endpoint that gets called
 * @param params - query parameters to add to the request
 * @param data - data to send with the request
 * @param headers - headers to send with the request
 * @param signal - optional abort signal to cancel the request
 */
export async function request<T>(
  method: "DELETE" | "GET" | "PATCH" | "POST" | "PUT",
  endpoint: string,
  params?: URLSearchParams | Record<string, string | number | undefined>,
  data?: Record<string, unknown>,
  headers?: Record<string, string>,
  signal?: AbortSignal,
): Promise<T> {
  // For "mutating" methods, update CSRF token.
  const isMutating = ["POST", "PUT", "PATCH", "DELETE"].includes(method);
  const csrfToken = isMutating
    ? await ensureCSRFToken()
    : getCookie("csrftoken");

  // Filter undefined params.
  let _params = params;
  if (params && !(params instanceof URLSearchParams)) {
    const obj = Object.fromEntries(
      Object.entries(params)
        .filter(([, v]) => v !== undefined)
        .map(([k, v]) => [k, (v || "").toString()]),
    );
    _params = new URLSearchParams(obj);
  }

  const base = API_BASE_URL + endpoint;
  const queryString = _params?.toString() || "";
  const url = queryString ? `${base}?${queryString}` : base;
  if (isMutating && !csrfToken) {
    console.error("CSRF token missing!", {
      cookieNames: document.cookie
        .split(";")
        .map((cookie) => cookie.trim().split("=")[0]),
      hostname: window.location.hostname,
      pathname: window.location.pathname,
    });
  }

  const response = await fetch(url, {
    credentials: "include",
    body: data ? JSON.stringify(data) : undefined,
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
      ...headers,
    },
    method,
    signal,
  });

  if (!response.ok) {
    throw response;
  }

  const contentType = response.headers.get("Content-Type") || "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  } else {
    // in case isf expected to return nothing, the caller should use `T = void`
    return undefined as T;
  }
}

/**
 * Makes sure a CSRF token (cookie) is set and returns it.
 *
 * The token is read from the `X-CSRFToken` response header instead of directly
 * from `document.cookie`: in WebKit a cookie set by a `fetch` response is not
 * always visible in `document.cookie` immediately, which caused (flaky) 403s.
 */
async function ensureCSRFToken(): Promise<string | null> {
  const response = await fetch(`${API_BASE_URL}/auth/ensure-csrf-token/`, {
    credentials: "include",
  });
  if (!response.ok) {
    throw response;
  }
  return response.headers.get("X-CSRFToken") || getCookie("csrftoken");
}

import { getCookie } from "@maykin-ui/client-common/cookie";

/** The base origin for all API requests. */
export const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

/** The base path for all API requests. */
export const API_PATH = import.meta.env.VITE_API_PATH || "/api/v1";

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
export async function request(
  method: "DELETE" | "GET" | "PATCH" | "POST" | "PUT",
  endpoint: string,
  params?: URLSearchParams | Record<string, string | number | undefined>,
  data?: Record<string, unknown>,
  headers?: Record<string, string>,
  signal?: AbortSignal,
) {
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
  const csrfToken = getCookie("csrftoken");

  const response = await fetch(url, {
    credentials: "include",
    body: data ? JSON.stringify(data) : undefined,
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || "",
      ...headers,
    },
    method: method,
    signal: signal,
  });

  if (response.ok) {
    return response;
  } else {
    throw response;
  }
}

import { cacheMemo } from "@maykin-ui/client-common";
import { request } from "~/api/request.ts";
import { components } from "~/types";

/**
 * API call for retrieving catalogi.
 * @param slug - the slug of the service to retrieve catalogi for
 * @param signal - optional abort signal to cancel the request */
export async function getCatalogiChoices(slug: string, signal?: AbortSignal) {
  return cacheMemo(
    "getCatalogiChoices",
    request<components["schemas"]["OBOption_str_"][]>,
    [
      "GET",
      `/service/${slug}/catalogi/choices/`,
      undefined,
      undefined,
      undefined,
      signal,
    ],
  );
}

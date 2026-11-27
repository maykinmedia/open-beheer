import { cacheMemo } from "@maykin-ui/client-common";
import { request } from "~/api/request.ts";
import { components } from "~/types";

/**
 * API call for retrieving service choices.
 */
export async function getServiceChoices(signal?: AbortSignal) {
  return cacheMemo(
    "getServiceChoices",
    request<components["schemas"]["OBOption_str_"][]>,
    ["GET", "/service/choices/", undefined, undefined, undefined, signal],
  );
}

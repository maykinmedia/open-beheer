import { cacheMemo } from "@maykin-ui/client-common";
import { request } from "~/api/request.ts";

export type ServiceChoice = {
  label: string;
  value: string;
};

/**
 * API call for retrieving service choices.
 */
export async function getServiceChoices() {
  return cacheMemo("getServiceChoices", request<ServiceChoice[]>, [
    "GET",
    "/service/choices/",
  ]);
}

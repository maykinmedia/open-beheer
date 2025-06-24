import { cacheMemo } from "@maykin-ui/client-common";
import { request } from "~/api/request.ts";

export type CatalogiChoice = {
  label: string;
  value: string;
};

/**
 * API call for retrieving catalogi.
 * @param slug - the slug of the service to retrieve catalogi for
 */
export async function getCatalogiChoices(slug: string) {
  return cacheMemo("getCatalogiChoices", request<CatalogiChoice[]>, [
    "GET",
    `/service/${slug}/catalogi/choices/`,
  ]);
}

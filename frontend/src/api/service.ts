import { request } from "~/api/request.ts";

export type ServiceChoice = {
  label: string;
  value: string;
};

/**
 * API call for retrieving service choices.
 */
export async function getServiceChoices() {
  return request<ServiceChoice[]>("GET", "/service/choices/");
}

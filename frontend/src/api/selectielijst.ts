import { request } from "~/api/request.ts";
import { components } from "~/types";

/**
 * Asynchronous function to fetch a result by provided URL through the backend.
 *
 * @param url - The url of the selectielijst resultaat.
 * @returns A tuple containing a `Promise` for the `LaxResultaat` and a
 * controller that can be used to cancel the request.
 */
export const getResultaatByUrl = (
  url: string,
): [Promise<components["schemas"]["LAXResultaat"]>, AbortController] => {
  const controller = new AbortController();
  const signal = controller.signal;

  const response = request<components["schemas"]["LAXResultaat"]>(
    "GET",
    `/selectielijst/resultaten/`,
    { url },
    undefined,
    undefined,
    signal,
  );
  return [response, controller];
};

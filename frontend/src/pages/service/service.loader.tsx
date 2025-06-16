import { LoaderFunctionArgs, replace } from "react-router";
import { getServiceChoices } from "~/api/service.ts";

export class NoServiceError extends Error {
  message = "No service was found in either parameters or API response.";
  code = "NO_SERVICE";
}

export type ServiceLoaderData = object;

/**
 * Service loader.
 * Loader data can be obtained using `useLoaderData()` in ServicePage.
 */
export async function serviceLoader({
  request,
}: LoaderFunctionArgs): Promise<ServiceLoaderData> {
  // No service specified, naively resolve the first available service.
  const serviceChoices = await getServiceChoices();
  const serviceChoice = serviceChoices?.[0];

  // No servie available, throw.
  if (!serviceChoice) {
    throw new NoServiceError();
  }

  // Redirect to resolved service.
  const url = new URL(request.url);
  const path = url.pathname;
  const redirectTo = "/" + serviceChoice.value + path;
  return replace(redirectTo);
}

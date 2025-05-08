import { LoaderFunction, redirect } from "react-router";

/**
 * Wraps an existing loader with authentication protection handling. Redirects
 * to the sign-in page if the request fails with a 403 status code.
 *
 * NOTE: This does not perform any actual authentication checks.
 *
 * @param wrappedLoader - Loader function to wrap.
 * @returns A function that, when called, executes the wrapped loader with the
 *  provided arguments.
 */
export function loginRequired<T extends object>(
  wrappedLoader: LoaderFunction,
): LoaderFunction<T | Response> {
  return async (loaderFunctionArgs, handlerCtx) => {
    try {
      return await wrappedLoader(loaderFunctionArgs, handlerCtx);
    } catch (e: unknown) {
      const url = new URL(window.location.toString());
      if ((e as Response)?.status === 403) {
        const next = url.searchParams.get("next")
          ? "/"
          : new URL(loaderFunctionArgs.request.url).pathname;
        return redirect(`/login?next=${next}`);
      }
      throw e;
    }
  };
}

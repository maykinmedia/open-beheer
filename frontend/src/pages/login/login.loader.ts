import { ensureCSRFToken } from "~/api";
import { getOIDCInfo } from "~/api/auth";

export type LoginLoaderData = object;

/**
 * Login loader.
 * Loader data can be obtained using `useLoaderData()` in LoginPage.
 */
export async function loginLoader(): Promise<LoginLoaderData> {
  const promiseOIDCInfo = getOIDCInfo();
  const promiseCSRFToken = ensureCSRFToken();

  const [oidcInfo] = await Promise.all([promiseOIDCInfo, promiseCSRFToken]);
  return { oidcInfo: oidcInfo };
}

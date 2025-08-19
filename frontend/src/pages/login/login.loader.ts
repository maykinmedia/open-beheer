import { getOIDCInfo } from "~/api/auth";

export type LoginLoaderData = object;

/**
 * Login loader.
 * Loader data can be obtained using `useLoaderData()` in LoginPage.
 */
export async function loginLoader(): Promise<LoginLoaderData> {
  const oidcInfo = await getOIDCInfo();

  return { oidcInfo: oidcInfo };
}

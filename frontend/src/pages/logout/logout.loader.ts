import { cacheDelete } from "@maykin-ui/client-common";
import { logout } from "~/api";

export type LogoutLoaderData = void;

/**
 * Logout loader.
 * Loader data can be obtained using `useLoaderData()` in LogoutPage.
 */
export async function logoutLoader(): Promise<LogoutLoaderData> {
  await cacheDelete("", true); // Clears all cache.
  sessionStorage.clear();

  try {
    await logout();
  } catch (e: unknown) {
    return await (e as Response).json();
  }
}

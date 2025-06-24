import { cacheDelete } from "@maykin-ui/client-common";
import { logout } from "~/api";

export type LogoutLoaderData = void;

/**
 * Logout loader.
 * Loader data can be obtained using `useLoaderData()` in LogoutPage.
 */
export async function logoutLoader(): Promise<LogoutLoaderData> {
  await cacheDelete("", true); // Clears all cache.
  await logout();
}

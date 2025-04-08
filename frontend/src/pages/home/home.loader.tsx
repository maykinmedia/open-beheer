export type HomeLoaderData = object;

/**
 * Home loader.
 * Loader data can be obtained using `useLoaderData()` in HomePage.
 */
export async function homeLoader(): Promise<HomeLoaderData> {
  return {};
}

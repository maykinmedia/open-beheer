import { LoaderFunctionArgs } from "react-router";
import { ZaaktypenLoaderData, zaaktypenLoader } from "~/pages";

export type ZaaktypeLoaderData = {
  demoData: ZaaktypenLoaderData["demoData"][number];
};

/**
 * Zaaktype loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypePage.
 */
export async function zaaktypeLoader({
  params,
}: LoaderFunctionArgs): Promise<ZaaktypeLoaderData> {
  // Probably not a great idea when implementing.
  const { demoData } = await zaaktypenLoader();
  return {
    demoData: demoData.find((row) => row.id === parseInt(params?.id || ""))!,
  };
}

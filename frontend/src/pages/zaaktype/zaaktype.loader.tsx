import { FieldSet } from "@maykin-ui/admin-ui";
import { LoaderFunctionArgs } from "react-router";
import { ZAAKTYPE_FIELDSETS, ZaakType, zaaktypenLoader } from "~/pages";

export type ZaaktypeLoaderData = {
  object: ZaakType;
  fieldsets: FieldSet<ZaakType>[];
};

/**
 * Zaaktype loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypePage.
 */
export async function zaaktypeLoader({
  params,
}: LoaderFunctionArgs): Promise<ZaaktypeLoaderData> {
  // Probably not a great idea when implementing.
  const { objectList } = await zaaktypenLoader();
  return {
    object: objectList.find((row) => row.id === parseInt(params?.id || ""))!,
    fieldsets: ZAAKTYPE_FIELDSETS,
  };
}

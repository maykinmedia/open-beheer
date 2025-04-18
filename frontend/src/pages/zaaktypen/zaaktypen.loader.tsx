import { FieldSet } from "@maykin-ui/admin-ui";
import { FIXTURE_ZAAKTYPEN } from "~/fixtures";
import { ZAAKTYPE_FIELDSETS } from "~/pages/zaaktype";
import { ZaakType } from "~/types";

export type ZaaktypenLoaderData = {
  objectList: ZaakType[];
  fieldsets: FieldSet<ZaakType>[];
};

/**
 * Zaaktypen loader.
 * Loader data can be obtained using `useLoaderData()` in ZaaktypenPage.
 */
export async function zaaktypenLoader(): Promise<ZaaktypenLoaderData> {
  const objectList = FIXTURE_ZAAKTYPEN;
  return { objectList, fieldsets: ZAAKTYPE_FIELDSETS };
}

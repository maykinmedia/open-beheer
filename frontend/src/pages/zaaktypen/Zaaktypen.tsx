import { useCallback } from "react";
import { useLoaderData, useLocation } from "react-router";
import { ZaaktypenLoaderData } from "~/pages";
import { ListView } from "~/views";

/**
 * Zaaktypen page
 */
export function ZaaktypenPage() {
  const loaderData = useLoaderData<ZaaktypenLoaderData>();
  const { pathname } = useLocation();

  /**
   * Splits `obj.url` into parts, using the last part as UUID.
   * @param obj - An object which implements a `url` key.
   */
  const getUUID = useCallback(
    (obj: { url: string }) => `${pathname}/${obj.url.split("/").reverse()[0]}`,
    [pathname],
  );

  return <ListView {...loaderData} getHref={getUUID} />;
}

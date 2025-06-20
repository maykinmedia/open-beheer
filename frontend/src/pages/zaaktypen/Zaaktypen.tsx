import { useCallback, useState } from "react";
import { useLoaderData, useLocation } from "react-router";
import {
  ZaaktypeFilter,
  ZaaktypeFilterValues,
  ZaaktypeStatusEnum,
} from "~/components";
import { useCombinedSearchParams } from "~/hooks";
import { ZaaktypenLoaderData } from "~/pages";
import { ListView } from "~/views";

/**
 * Zaaktypen page
 */
export function ZaaktypenPage() {
  const loaderData = useLoaderData<ZaaktypenLoaderData>();
  const { pathname } = useLocation();
  const [searchParams, setCombinedSearchParams] = useCombinedSearchParams(0);
  const [filterState, setFilterState] = useState<Record<string, string | null>>(
    Object.fromEntries(searchParams),
  );

  /**
   * Splits `obj.url` into parts, using the last part as UUID.
   * @param obj - An object which implements a `url` key.
   */
  const getUUID = useCallback(
    (obj: { url: string }) => `${pathname}/${obj.url.split("/").reverse()[0]}`,
    [pathname],
  );

  /**
   * Updates the query string with the filter values.
   * @param data - The filter values.
   */
  const handleSubmit = (data: ZaaktypeFilterValues) => {
    setFilterState(data);
    setCombinedSearchParams(data as URLSearchParams);
  };

  return (
    <ListView
      {...loaderData}
      getHref={getUUID}
      toolbarItems={[
        <ZaaktypeFilter
          key="zaaktypefilter"
          status={
            (filterState.status || "").toLowerCase() as ZaaktypeStatusEnum
          }
          trefwoorden={filterState.trefwoorden}
          onSubmit={handleSubmit}
        />,
      ]}
    />
  );
}

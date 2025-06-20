import { useState } from "react";
import { useLoaderData } from "react-router";
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
  const [searchParams, setCombinedSearchParams] = useCombinedSearchParams(0);
  const [filterState, setFilterState] = useState<Record<string, string | null>>(
    Object.fromEntries(searchParams),
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

import { ButtonLink, Outline } from "@maykin-ui/admin-ui";
import { useCallback } from "react";
import { useLoaderData, useLocation } from "react-router";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { components } from "~/types";
import { ListView } from "~/views";

import { InformatieObjectTypenLoaderData } from "./informatieobjecttype.loader";

export function InformatieObjectTypenPage() {
  const loaderData = useLoaderData<InformatieObjectTypenLoaderData>();
  const { pathname } = useLocation();

  const getAbsolutePath = useCallback(
    (obj: components["schemas"]["InformatieObjectTypeSummary"]) => {
      const iotUuid = obj.url ? getUUIDFromString(obj.url) : null;
      return `${pathname}/${iotUuid}`;
    },
    [pathname],
  );

  return (
    <ListView
      {...loaderData}
      getHref={getAbsolutePath}
      toolbarItems={[
        // TODO: filters
        <ButtonLink
          href="informatieobjecttypen/create"
          key="create-informatieobjecttype"
          variant="primary"
        >
          <Outline.PlusIcon /> Nieuw informatieobjecttype
        </ButtonLink>,
      ]}
    />
  );
}

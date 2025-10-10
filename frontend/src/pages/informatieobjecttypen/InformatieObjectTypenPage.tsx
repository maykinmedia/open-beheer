import { Button, Outline } from "@maykin-ui/admin-ui";
import { useCallback } from "react";
import { NavLink, useLoaderData, useLocation } from "react-router";
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
        <Button
          key="create-informatieobjecttype"
          // TODO: Fix styling
          // variant="primary"
        >
          <NavLink to="create">
            <Outline.PlusIcon /> Nieuw informatieobjecttype
          </NavLink>
        </Button>,
      ]}
    />
  );
}

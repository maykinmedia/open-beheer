import { useLoaderData, useLocation } from "react-router";
import { InformatieObjectTypenLoaderData } from "./informatieobjecttype.loader";
import { ListView } from "~/views";
import { ButtonLink, Outline } from "@maykin-ui/admin-ui";
import { useCallback } from "react";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { components } from "~/types";


export function InformatieObjectTypenPage() {
    const loaderData = useLoaderData<InformatieObjectTypenLoaderData>();
    const { pathname } = useLocation();

    const getAbsolutePath = useCallback(
        (obj: components["schemas"]["InformatieObjectTypeSummary"]) => {
            console.log(obj);
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


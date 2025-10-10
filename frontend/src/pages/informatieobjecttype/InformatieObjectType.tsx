import { AttributeGrid, Body, CardBaseTemplate, H2 } from "@maykin-ui/admin-ui";
import { ucFirst } from "@maykin-ui/client-common";
import { useMemo } from "react";
import { useLoaderData } from "react-router";
import { useBreadcrumbItems } from "~/hooks";
import { convertFieldsetsToTabConfig } from "~/lib";
import { components } from "~/types";

import { AttributeGridSection, TabConfig } from "../zaaktype";
import { InformatieObjectTypeLoaderData } from "./informatieobjecttype.loader";

type BackendIOT = components["schemas"]["InformatieObjectType"];

export function InformatieObjectTypePage() {
  const { fields, fieldsets, result } =
    useLoaderData() as InformatieObjectTypeLoaderData;
  const breadcrumbItems = useBreadcrumbItems();

  const fieldSetConfigs = useMemo<TabConfig<BackendIOT>[]>(
    convertFieldsetsToTabConfig<BackendIOT>(fieldsets),
    [JSON.stringify([fields, fieldsets])],
  );

  // We know that the IOT does not have expansions, 
  // so we can narrow the type further
  const section = fieldSetConfigs[0]
    .sections[0] as AttributeGridSection<BackendIOT>;

  return (
    <CardBaseTemplate
      breadcrumbItems={breadcrumbItems}
      cardProps={{
        justify: "space-between",
      }}
    >
      <Body fullHeight>
        <H2>{ucFirst(result.omschrijving)}</H2>

        <AttributeGrid
          object={result}
          editable={false}
          editing={false}
          fieldsets={section.fieldsets}
        />
      </Body>
    </CardBaseTemplate>
  );
}

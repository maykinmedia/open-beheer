import {
  AttributeGrid,
  Body,
  CardBaseTemplate,
  H2,
  Solid,
  Toolbar,
} from "@maykin-ui/admin-ui";
import { ucFirst } from "@maykin-ui/client-common";
import { useCallback, useMemo } from "react";
import { useLoaderData } from "react-router";
import { useBreadcrumbItems, useCombinedSearchParams } from "~/hooks";
import { useSubmitAction } from "~/hooks/useSubmitAction";
import { convertFieldsetsToTabConfig } from "~/lib";
import { components } from "~/types";

import { AttributeGridSection, TabConfig } from "../zaaktype";
import { InformatieObjectTypeAction } from "./informatieobjecttype.action";
import { InformatieObjectTypeLoaderData } from "./informatieobjecttype.loader";

type BackendIOT = components["schemas"]["InformatieObjectType"];

export function InformatieObjectTypePage() {
  const { fields, fieldsets, result } =
    useLoaderData() as InformatieObjectTypeLoaderData;
  const breadcrumbItems = useBreadcrumbItems();
  const submitAction = useSubmitAction<InformatieObjectTypeAction>();
  const [combinedSearchParams] = useCombinedSearchParams();
  const isEditing = Boolean(combinedSearchParams.get("editing"));

  const fieldSetConfigs = useMemo<TabConfig<BackendIOT>[]>(
    convertFieldsetsToTabConfig<BackendIOT>(fieldsets),
    [JSON.stringify([fields, fieldsets])],
  );

  const onEdit = useCallback<React.MouseEventHandler>(() => {
    // invariant(conceptVersion, "concept version (uuid) must be set");

    submitAction({
      type: "EDIT_VERSION",
      payload: {},
    });
  }, []);

  // We know that the IOT does not have expansions,
  // so we can narrow the type further
  const section = fieldSetConfigs[0]
    .sections[0] as AttributeGridSection<BackendIOT>;

  const buttons = result.concept
    ? [
        {
          children: (
            <>
              <Solid.PencilSquareIcon />
              Bewerken
            </>
          ),
          variant: "primary",
          onClick: onEdit,
        },
      ]
    : [];

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
          editing={isEditing}
          fieldsets={section.fieldsets}
        />
      </Body>

      <Toolbar
        align="end"
        pad
        variant="transparent"
        sticky={"bottom"}
        items={buttons}
      ></Toolbar>
    </CardBaseTemplate>
  );
}

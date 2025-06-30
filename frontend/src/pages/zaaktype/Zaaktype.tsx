import {
  AttributeGrid,
  Body,
  CardBaseTemplate,
  FieldSet,
  H2,
  Tab,
  Tabs,
} from "@maykin-ui/admin-ui";
import { ucFirst } from "@maykin-ui/client-common";
import { useMemo } from "react";
import { useLoaderData } from "react-router";
import { useBreadcrumbItems } from "~/hooks";
import { ZaaktypeLoaderData } from "~/pages";
import { components } from "~/types";

const FIELDSETS_OVERVIEW: FieldSet<components["schemas"]["ZaakType"]>[] = [
  [
    "",
    {
      fields: ["identificatie"],
      span: 12,
    },
  ],

  [
    "",
    {
      fields: ["doel"],
      span: 6,
    },
  ],

  [
    "",
    {
      fields: ["omschrijving"],
      span: 6,
    },
  ],

  [
    "",
    {
      fields: ["statustypen"],
      span: 4,
    },
  ],

  [
    "",
    {
      fields: ["informatieobjecttypen"],
      span: 4,
    },
  ],

  [
    "",
    {
      fields: ["roltypen"],
      span: 4,
    },
  ],

  [
    "",
    {
      fields: ["resultaattypen"],
      span: 4,
    },
  ],

  [
    "",
    {
      fields: ["eigenschappen"],
      span: 4,
    },
  ],

  [
    "",
    {
      fields: ["gerelateerdeZaaktypen"],
      span: 4,
    },
  ],

  [
    "",
    {
      fields: ["zaakobjecttypen"],
      span: 4,
    },
  ],

  [
    "",
    {
      fields: ["selectielijstProcestype"],
      span: 4,
    },
  ],
];

/**
 * Zaaktype page
 */
export function ZaaktypePage() {
  const breadcrumbItems = useBreadcrumbItems();
  const { result } = useLoaderData() as ZaaktypeLoaderData;

  // Stringify arrays.
  // TODO: Investigate better approach when _expand logic lands.
  const object = useMemo(
    () =>
      Object.fromEntries(
        Object.entries(result).map(([k, v]) => [
          k,
          Array.isArray(v) ? v.join(", ") : (v || "").toString(),
        ]),
      ),
    [result],
  );

  return (
    <CardBaseTemplate breadcrumbItems={breadcrumbItems}>
      <Body>
        <H2>{ucFirst(result.omschrijving)}</H2>
        <Tabs>
          <Tab label="Overzicht">
            <AttributeGrid
              object={object}
              fieldsets={
                FIELDSETS_OVERVIEW as unknown as FieldSet<typeof object>[]
              }
            ></AttributeGrid>
          </Tab>
        </Tabs>
      </Body>
    </CardBaseTemplate>
  );
}

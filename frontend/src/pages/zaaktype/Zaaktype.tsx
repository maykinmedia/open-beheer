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
import { useCallback, useMemo } from "react";
import { useLoaderData, useNavigate } from "react-router";
import { VersionSelector } from "~/components/VersionSelector";
import { useBreadcrumbItems } from "~/hooks";
import { getZaaktypeUUID } from "~/lib";
import { ZaaktypeLoaderData } from "~/pages";
import { components } from "~/types";

const FIELDSETS_OVERVIEW: FieldSet<components["schemas"]["ZaakType"]>[] = [
  [
    "",
    {
      fields: ["identificatie", "omschrijving"],
      span: 12,
      colSpan: 6,
    },
  ],

  [
    "",
    {
      fields: ["doel"],
      span: 12,
    },
  ],

  [
    "",
    {
      fields: [
        "statustypen",
        "informatieobjecttypen",
        "resultaattypen",
        "eigenschappen",
        "zaakobjecttypen",
        "selectielijstProcestype",
      ],
      span: 12,
      colSpan: 6,
    },
  ],
];

/**
 * Zaaktype page
 */
export function ZaaktypePage() {
  const navigate = useNavigate();
  const breadcrumbItems = useBreadcrumbItems();
  const { result, versions } = useLoaderData() as ZaaktypeLoaderData;

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

  /**
   * Gets called when a version is selected.
   */
  const handleVersionChange = useCallback(
    (version: components["schemas"]["VersionSummary"]) => {
      navigate(`../${version.uuid}`);
    },
    [versions],
  );

  return (
    <CardBaseTemplate breadcrumbItems={breadcrumbItems}>
      <Body>
        <H2>
          {ucFirst(result.identificatie || "")}{" "}
          {result.omschrijving ? `(${result.omschrijving})` : null}
        </H2>

        {versions && (
          <VersionSelector
            currentVersionUUID={getZaaktypeUUID(result)}
            versions={versions}
            onVersionChange={handleVersionChange}
          />
        )}

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

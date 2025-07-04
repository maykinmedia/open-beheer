import {
  AttributeGrid,
  Badge,
  Body,
  CardBaseTemplate,
  DataGrid,
  H2,
  Tab,
  Tabs,
} from "@maykin-ui/admin-ui";
import { ucFirst } from "@maykin-ui/client-common";
import { useLoaderData } from "react-router";
import { useBreadcrumbItems } from "~/hooks";
import {
  ExpandFieldConfig,
  FIELDSETS_GENERAL,
  FIELDSETS_OVERVIEW,
  TABS_CONFIG,
  ZaaktypeLoaderData,
} from "~/pages";

/**
 * Zaaktype page
 */
export function ZaaktypePage() {
  const breadcrumbItems = useBreadcrumbItems();
  const { result } = useLoaderData() as ZaaktypeLoaderData;

  function buildExpandedObject(
    result: ZaaktypeLoaderData["result"],
    context: keyof typeof TABS_CONFIG,
  ) {
    const entries = Object.entries(result).map(([key, value]) => {
      const typedKey = key as keyof ZaaktypeLoaderData["result"]["_expand"];
      const expandedItems = result._expand?.[typedKey];

      const config = TABS_CONFIG[context]?.[typedKey];

      function isStringArray(arr: unknown): arr is string[] {
        return Array.isArray(arr) && arr.every((el) => typeof el === "string");
      }

      function getDisplayValue(
        item: Record<string, unknown>,
        config?: ExpandFieldConfig,
      ): string | Record<string, unknown> | null {
        if (!config || config.type === "priority") {
          const keys = config?.keys ?? ["omschrijving", "naam"];
          for (const key of keys) {
            const val = item[key];
            if (typeof val === "string" && val) return val;
          }
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-expect-error
          return (item as unknown).url ?? null;
        }

        if (config.type === "object") {
          const result: Record<string, unknown> = {};
          for (const key of config.keys) {
            result[key] = item[key];
          }
          return result;
        }

        return null;
      }

      if (Array.isArray(value) && Array.isArray(expandedItems)) {
        const urlToDisplay = Object.fromEntries(
          expandedItems.map((item) => [
            item.url,
            getDisplayValue(item, config),
          ]),
        );

        if (isStringArray(value)) {
          if (!config || config.type === "priority") {
            const badges = (
              <>
                {value.map((url) => {
                  const display = urlToDisplay[url];

                  if (typeof display === "string") {
                    return <Badge key={url}>{display}</Badge>;
                  }

                  if (display && typeof display === "object") {
                    return (
                      <Badge key={url}>
                        {Object.values(display).join(" - ")}
                      </Badge>
                    );
                  }

                  return <Badge key={url}>{url}</Badge>;
                })}
              </>
            );
            return [key, badges];
          }

          if (config.type === "object") {
            const objectArray = value.map((url) => {
              const display = urlToDisplay[url];
              return typeof display === "object" ? display : { url };
            });
            return [key, objectArray];
          }
        }
      }

      return [key, value?.toString() ?? null];
    });

    return Object.fromEntries(entries);
  }

  const overzichtObject = buildExpandedObject(result, "Overzicht");
  const statustypenObject = buildExpandedObject(result, "Statustypen");

  return (
    <CardBaseTemplate breadcrumbItems={breadcrumbItems}>
      <Body>
        <H2>{ucFirst(result.omschrijving)}</H2>
        <Tabs>
          <Tab label="Overzicht">
            <AttributeGrid
              object={overzichtObject}
              fieldsets={FIELDSETS_OVERVIEW}
            ></AttributeGrid>
          </Tab>
          <Tab label="Algemene gegevens">
            <AttributeGrid
              object={result}
              fieldsets={FIELDSETS_GENERAL}
            ></AttributeGrid>
          </Tab>
          <Tab label="Statustypen">
            <DataGrid objectList={statustypenObject.statustypen}></DataGrid>
          </Tab>
        </Tabs>
      </Body>
    </CardBaseTemplate>
  );
}

import {
  Button,
  DataGrid,
  Form,
  FormControlProps,
  Outline,
} from "@maykin-ui/admin-ui";
import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router";
import { SERVICE_PARAM } from "~/App.tsx";
import { RelatedObjectBadge } from "~/components/related/RelatedObjectBadge.tsx";
import { useCombinedSearchParams } from "~/hooks";
import { useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import { getZaaktypeUUID } from "~/lib";
import { BaseTabSection, TabConfig } from "~/pages";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { ExpandItemKeys, RelatedObject } from "~/types";

type RelatedObjectRendererProps<T extends object> = {
  relatedObject: object | object[]; // TODO: Can improve typing
  view: TabConfig<T>["view"];
  expandFields: BaseTabSection<T>["expandFields"];
  field: ExpandItemKeys<T>;
  zaaktypeUuid: string;
};

/**
 * Renders either a DataGrid or a list of badges for a set of related objects,
 * depending on the tab configuration.
 *
 * @param relatedObjects - The array of objects to render
 * @param view - The view type, either "DataGrid" or "AttributeGrid"
 */
export function RelatedObjectRenderer<T extends object>({
  relatedObject,
  view,
  expandFields,
  field,
  zaaktypeUuid,
}: RelatedObjectRendererProps<T>) {
  const [combinedSearchParams] = useCombinedSearchParams();
  const [addNewValueState, setAddNewValueState] = useState<string | null>(null);
  // TODO: Editable on `url` needs to be false
  const params = useParams();
  const serviceSlug = params[SERVICE_PARAM];
  const submitAction = useSubmitAction<ZaaktypeAction>();
  const [relatedObjectChoices, setRelatedObjectChoices] = useState<
    RelatedObject<T>[]
  >([]);

  useEffect(() => {
    const controller = new AbortController();

    const fetchChoices = async () => {
      try {
        // const choices = await getRelatedObjectTemplateChoices(field);
        // if (choices) {
        //   setRelatedObjectChoices(choices);
        // }
      } catch (error) {
        console.error("Failed to fetch choices:", error);
      }
    };

    void fetchChoices();

    return () => {
      controller.abort();
    };
  }, [field]);

  const onAdd = (url: string) => {
    const foundRelatedObject = relatedObjectChoices.find(
      (choice: { url?: string }) => choice.url === url,
    );
    if (!foundRelatedObject) {
      console.warn(`No choice found for value: ${url}`);
      return;
    }
    if (!serviceSlug) {
      console.warn("Service slug is not defined.");
      return;
    }
    submitAction({
      type: "ADD_RELATED_OBJECT",
      payload: {
        serviceSlug: serviceSlug,
        zaaktypeUuid: zaaktypeUuid,
        relatedObjectKey: field,
        relatedObject: foundRelatedObject,
      },
    });
  };

  const onEdit = (relatedObject: RelatedObject<T>) => {
    if (!serviceSlug) {
      console.warn("Service slug is not defined.");
      return;
    }
    submitAction({
      type: "EDIT_RELATED_OBJECT",
      payload: {
        serviceSlug: serviceSlug,
        zaaktypeUuid: zaaktypeUuid,
        relatedObjectKey: field,
        relatedObject: relatedObject,
      },
    });
  };

  const onDelete = (relatedObject: RelatedObject<T>) => {
    if (!serviceSlug) {
      console.warn("Service slug is not defined.");
      return;
    }
    submitAction({
      type: "DELETE_RELATED_OBJECT",
      payload: {
        serviceSlug: serviceSlug,
        zaaktypeUuid: zaaktypeUuid,
        relatedObjectKey: field,
        relatedObjectUuid: getZaaktypeUUID(relatedObject) ?? "",
      },
    });
  };

  const fields: FormControlProps[] = [
    {
      name: `${field}-toevoegen`,
      label: `Voeg ${field} toe`,
      type: "text",
      placeholder: "Selecteer...",
      value: addNewValueState,
      options: relatedObjectChoices.map(
        (choice: { url?: string; omschrijving?: string }) => ({
          label: choice.omschrijving || choice.url || "Onbekend",
          value: choice.url || "",
        }),
      ),
      onChange: (e: ChangeEvent<HTMLSelectElement>) =>
        setAddNewValueState(e.target.value),
    },
  ];

  const augmentedObjectList = useMemo(
    () =>
      Array.isArray(relatedObject)
        ? relatedObject.map((row) => ({
            ...row,
            action: (
              <Button
                variant="danger"
                size="xs"
                onClick={() => onDelete(row as RelatedObject<T>)}
              >
                <Outline.TrashIcon />
              </Button>
            ),
          }))
        : [],
    [relatedObject],
  );

  if (!Array.isArray(relatedObject)) {
    if (!relatedObject) return null;

    return (
      <RelatedObjectBadge
        relatedObject={relatedObject}
        allowedFields={expandFields}
      />
    );
  }

  if (view === "DataGrid") {
    return (
      <>
        <DataGrid<(typeof relatedObject)[number]>
          objectList={augmentedObjectList}
          editable={Boolean(combinedSearchParams.get("editing"))}
          fields={[...expandFields, "action"]}
          onEdit={(data) => {
            const _data = data as RelatedObject<T>;
            onEdit(_data);
          }}
          urlFields={[]}
        />
        <Form // TODO: New select/combobox according to design is necessary.
          buttonProps={{ pad: "h" }}
          fields={fields}
          showRequiredExplanation={false}
          labelSubmit="Toevoegen"
          onSubmit={() => onAdd?.(addNewValueState || "")}
        />
      </>
    );
  }

  // Assume for attribute grid.
  return relatedObject.map((relatedObject, index) => (
    <RelatedObjectBadge
      key={typeof relatedObject.url === "string" ? relatedObject.url : index}
      relatedObject={relatedObject}
      allowedFields={expandFields}
    />
  ));
}

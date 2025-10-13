import {
  AttributeGrid,
  Body,
  CardBaseTemplate,
  Form,
  FormField,
  H2,
  Outline,
  Solid,
  Toolbar,
} from "@maykin-ui/admin-ui";
import { ucFirst } from "@maykin-ui/client-common";
import { FormEvent, useCallback, useMemo } from "react";
import { useLoaderData } from "react-router";
import { useBreadcrumbItems, useCombinedSearchParams } from "~/hooks";
import { useSubmitAction } from "~/hooks/useSubmitAction";

import {
  BackendIOT,
  InformatieObjectTypeAction,
} from "./informatieobjecttype.action";
import { InformatieObjectTypeLoaderData } from "./informatieobjecttype.loader";

export const INFORMATIEOBJECTTYPE_UPDATE_FIELDS: FormField[] = [
  { name: "omschrijving", type: "text", label: "Omschrijving", required: true },
  {
    name: "vertrouwelijkheidaanduiding",
    type: "string",
    label: "Vertrouwelijkheidaanduiding",
    required: true,
  },
  {
    name: "beginGeldigheid",
    type: "datepicker",
    label: "Begin geldigheid",
    required: true,
  },
];

export function InformatieObjectTypePage() {
  const { fields, fieldsets, result } =
    useLoaderData() as InformatieObjectTypeLoaderData;
  const breadcrumbItems = useBreadcrumbItems();
  const submitAction = useSubmitAction<InformatieObjectTypeAction>();
  const [combinedSearchParams] = useCombinedSearchParams();
  const isEditing = Boolean(combinedSearchParams.get("editing"));

  const formFields = useMemo((): FormField[] => {
    return fields
      .map((field) => {
        if (
          !INFORMATIEOBJECTTYPE_UPDATE_FIELDS.map((f) => f.name).includes(
            field.name,
          )
        )
          return;

        const overrides = INFORMATIEOBJECTTYPE_UPDATE_FIELDS.find(
          (iotFieldOverride) => iotFieldOverride.name === field.name,
        );

        return {
          ...field,
          ...overrides,
        };
      })
      .filter((f) => f !== undefined);
  }, [fields, fieldsets]);

  const onEdit = useCallback<React.MouseEventHandler>(() => {
    submitAction({
      type: "SET_EDIT_MODE_ON",
      payload: {},
    });
  }, []);

  const onCancel = useCallback<React.MouseEventHandler>((event) => {
    event.preventDefault();

    submitAction({
      type: "SET_EDIT_MODE_OFF",
      payload: {},
    });
  }, []);

  const onSubmit = async (
    event: FormEvent<HTMLFormElement>,
    data: Partial<BackendIOT>,
  ) => {
    event.preventDefault();

    await submitAction({
      type: "UPDATE",
      payload: data,
    });
  };

  return (
    <CardBaseTemplate
      breadcrumbItems={breadcrumbItems}
      cardProps={{
        justify: "space-between",
      }}
    >
      <Body fullHeight>
        <H2>{ucFirst(result.omschrijving)}</H2>

        {isEditing ? (
          <Form
            key={`informatieobjecttype-edit-form`}
            aria-label="Informatieobjecttype aanpassen"
            fields={formFields}
            justify="stretch"
            validateOnChange
            showActions={true}
            onSubmit={onSubmit}
            initialValues={{
              omschrijving: result.omschrijving,
              vertrouwelijkheidaanduiding: result.vertrouwelijkheidaanduiding,
              beginGeldigheid: result.beginGeldigheid,
            }}
            labelSubmit="Opslaan"
            secondaryActions={[
              {
                children: (
                  <>
                    <Outline.NoSymbolIcon />
                    Annuleren
                  </>
                ),
                variant: "danger",
                onClick: onCancel,
              },
            ]}
          />
        ) : (
          <AttributeGrid
            object={result}
            editable={false}
            editing={false}
            fieldsets={fieldsets}
          />
        )}
      </Body>

      <Toolbar
        align="end"
        pad
        variant="transparent"
        sticky={"bottom"}
        items={
          result.concept && !isEditing
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
            : []
        }
      ></Toolbar>
    </CardBaseTemplate>
  );
}

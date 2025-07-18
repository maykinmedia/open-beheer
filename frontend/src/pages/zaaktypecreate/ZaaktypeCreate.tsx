import {
  A,
  Body,
  Button,
  Card,
  CardBaseTemplate,
  Column,
  Form,
  FormField,
  Grid,
  H1,
  H2,
  Modal,
  Outline,
  P,
  SerializedFormData,
  Ul,
  validateForm,
} from "@maykin-ui/admin-ui";
import React, { FormEvent, useCallback, useEffect } from "react";
import { useActionData, useLoaderData, useParams } from "react-router";
import { CATALOGUS_PARAM, SERVICE_PARAM } from "~/App.tsx";
import { useBreadcrumbItems } from "~/hooks";
import { useSubmitAction } from "~/hooks/useSubmitAction.ts";
import {
  ZaakTypeCreateAction,
  ZaaktypeCreateActionPayload,
  ZaaktypeCreateLoaderData,
} from "~/pages";
import { components } from "~/types";

import "./zaaktypeCreate.styles.css";

export function ZaaktypeCreatePage() {
  const { results } = useLoaderData<ZaaktypeCreateLoaderData>();
  const breadcrumbItems = useBreadcrumbItems();
  const submitAction = useSubmitAction<ZaakTypeCreateAction>(false);
  const params = useParams();
  const serviceSlug = params[SERVICE_PARAM];
  const catalogusSlug = params[CATALOGUS_PARAM];
  const actionData = useActionData() as components["schemas"]["ZGWError"];

  const [isFillingForm, setIsFillingForm] = React.useState(false);
  const [valuesState, setValuesState] = React.useState<
    Partial<ZaaktypeCreateLoaderData["results"][0]>
  >({});
  const [nonFieldErrors, setNonFieldErrors] = React.useState<
    string[] | undefined
  >();

  const [isValidState, setIsValidState] = React.useState(false);

  useEffect(() => {
    if (actionData?.invalidParams?.length) {
      setNonFieldErrors(
        actionData.invalidParams.map(
          (error) =>
            `Het veld "${error.name}" is niet correct: ${error.reason}`,
        ),
      );
    } else {
      setNonFieldErrors(undefined);
    }
  }, [actionData]);

  const fields: FormField[] = [
    {
      label: "Identificatienummer",
      name: "identificatie",
      type: "text",
      defaultValue: valuesState.waarden?.identificatie || "",
      required: true,
    },
    {
      label: "Omschrijving",
      name: "omschrijvingGeneriek",
      defaultValue: valuesState.waarden?.omschrijvingGeneriek || "",
      type: "text",
      required: true,
    },
  ];

  const handleSelectTemplate = useCallback(
    (uuid: string | null) => {
      setValuesState({});
      setNonFieldErrors(undefined);
      if (uuid) {
        const selectedResult = results.find((result) => result.uuid === uuid);
        if (selectedResult) {
          setValuesState({ ...selectedResult });
        }
      } else {
        setValuesState({});
      }
    },
    [results],
  );

  const handleValidate = useCallback(
    (values: SerializedFormData, fields: FormField[]) => {
      const errors = validateForm(values, fields);
      const isValid = Object.keys(errors).length === 0;
      setIsValidState(isValid);
      return errors;
    },
    [valuesState],
  );

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>, data: SerializedFormData) => {
      if (!isValidState || !serviceSlug || !catalogusSlug) {
        console.warn(
          "Form is not valid or serviceSlug/catalogusSlug is missing.",
          {
            isValidState,
            serviceSlug,
          },
        );
        setNonFieldErrors([
          "Het formulier is niet correct ingevuld of de service/cataloog is niet ingesteld.",
        ]);
        event.preventDefault();
        return;
      }
      const finalPayload: ZaaktypeCreateActionPayload = {
        zaaktype: {
          ...valuesState.waarden,
          ...data,
        },
        serviceSlug: serviceSlug,
        catalogusSlug: catalogusSlug,
      };

      await submitAction({
        type: "ZAAKTYPE_CREATE",
        payload: finalPayload,
      });
    },
    [isValidState],
  );

  return (
    <CardBaseTemplate breadcrumbItems={breadcrumbItems}>
      <Modal open={isFillingForm} onClose={() => setIsFillingForm(false)}>
        <Body>
          <H2>Er zijn nog enkele velden nodig om het zaaktype aan te maken</H2>
          <Form
            key={`zaaktypecreate-form-${valuesState.uuid || ""}`}
            aria-label="Zaaktype aanmaken"
            nonFieldErrors={nonFieldErrors}
            fields={fields}
            validateOnChange
            showActions={true}
            validate={handleValidate}
            onSubmit={handleSubmit}
          />
        </Body>
      </Modal>
      <Body>
        <Grid fullHeight={true}>
          <Column span={12}>
            <H1>Kies een sjabloon</H1>
          </Column>
          <Column span={6}>
            <P>
              Maak een nieuw zaaktype aan door te starten vanaf een sjabloon of
              met een blanco opzet. Kies de variant die het beste past bij het
              soort proces dat je wilt inrichten
            </P>
          </Column>
          <Column span={6} />

          {results.map((result) => (
            <Column
              span={3}
              key={result.uuid}
              className="zaaktypecreate__card-column-wrapper"
            >
              <ZaaktypeCreateCard
                result={result}
                selectedTemplate={valuesState.uuid || null}
                setSelectedTemplate={handleSelectTemplate}
              />
            </Column>
          ))}
          <Column span={12}>
            <Button
              variant="secondary"
              disabled={!valuesState.uuid}
              onClick={() => setIsFillingForm(true)}
            >
              Gebruik dit sjabloon
            </Button>
            <P>
              Of kopieer een <A href="/zaaktypen">bestaand zaaktype</A>
            </P>
          </Column>
        </Grid>
      </Body>
    </CardBaseTemplate>
  );
}

type ZaaktypeCreateCardProps = {
  result: ZaaktypeCreateLoaderData["results"][number];
  selectedTemplate: string | null;
  setSelectedTemplate: (uuid: string | null) => void;
};

export const ZaaktypeCreateCard: React.FC<ZaaktypeCreateCardProps> = ({
  result,
  selectedTemplate,
  setSelectedTemplate,
}) => {
  return (
    <Card
      className="zaaktypecreate__card"
      onClick={() => setSelectedTemplate(result.uuid || null)}
      border={true}
      title={result.naam}
      actions={[
        {
          type: "radio",
          name: `zaaktypecreate-${result.naam}`,
          value: result.uuid,
          checked: selectedTemplate === result.uuid,
        },
      ]}
    >
      <Body fullHeight={true} className="zaaktypecreate__card-body">
        <P>{result.omschrijving}</P>
        {result.voorbeelden.length > 0 && (
          <Ul>
            {result.voorbeelden.map((voorbeeld) => (
              <li key={voorbeeld}>{voorbeeld}</li>
            ))}
          </Ul>
        )}
        <div className="zaaktypecreate__link">
          <A href={``}>
            <Outline.EyeIcon /> Bekijk voorbeeld
          </A>
        </div>
      </Body>
    </Card>
  );
};

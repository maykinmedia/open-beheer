import {
  FormField,
  FormValidator,
  SerializedFormData,
  validateForm,
} from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import React, { FormEvent, useCallback, useContext, useEffect } from "react";
import { useActionData, useLoaderData, useParams } from "react-router";
import { CATALOGUS_PARAM, OBContext, SERVICE_PARAM } from "~/App.tsx";
import { useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { ZAAKTYPE_CREATE_BASE_FIELDS } from "~/lib/zaaktype/zaaktypeCreate.ts";
import {
  ZaakTypeCreateAction,
  ZaaktypeCreateActionPayload,
  ZaaktypeCreateLoaderData,
} from "~/pages";
import { components } from "~/types";
import { CreateView } from "~/views/CreateView";

type ZaaktypeTemplate =
  components["schemas"]["Sjabloon_OptionalExpandableZaakTypeRequest_"] & {
    uuid: string;
  };

export function ZaaktypeCreatePage() {
  const obContext = useContext(OBContext);
  const { results } = useLoaderData<ZaaktypeCreateLoaderData>();

  const submitAction = useSubmitAction<ZaakTypeCreateAction>(false);
  const params = useParams();
  const serviceSlug = params[SERVICE_PARAM];
  const catalogusUUID = params[CATALOGUS_PARAM];
  const catalogusURL = obContext.catalogiChoices.find(
    (c) => getUUIDFromString(c.value) === catalogusUUID,
  )?.value;

  const actionData = useActionData() as components["schemas"]["ZGWError"];

  const [nonFieldErrors, setNonFieldErrors] = React.useState<
    string[] | undefined
  >();

  const [isValidState, setIsValidState] = React.useState(false);
  const fields = ZAAKTYPE_CREATE_BASE_FIELDS;

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

  const handleValidate = useCallback<FormValidator>(
    (values: object, fields: FormField[], validators) => {
      const errors = validateForm(values, fields, validators);
      const isValid = Object.keys(errors).length === 0;
      setIsValidState(isValid);
      return errors;
    },
    [],
  );

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>, data: SerializedFormData) => {
      if (!isValidState || !serviceSlug || !catalogusUUID) {
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

      invariant(catalogusURL, "Unable to determine catalogus url!");
      const finalPayload: ZaaktypeCreateActionPayload = {
        zaaktype: data,
        serviceSlug: serviceSlug,
        catalogus: catalogusURL,
      };

      await submitAction({
        type: "ZAAKTYPE_CREATE",
        payload: finalPayload,
      });
    },
    [isValidState],
  );

  const modalText =
    "Je staat op het punt een nieuw zaaktype te starten. Geef een identificatie en omschrijving op. Deze twee gegevens vormen de basis van je nieuwe zaaktype.";

  const templates = results.filter((result): result is ZaaktypeTemplate =>
    Boolean(result.uuid),
  );

  return (
    <CreateView<ZaaktypeTemplate>
      formFields={fields}
      modalText={modalText}
      nonFieldErrors={nonFieldErrors}
      resourceName="zaaktype"
      templates={templates}
      onValidate={handleValidate}
      onSubmit={handleSubmit}
    />
  );
}

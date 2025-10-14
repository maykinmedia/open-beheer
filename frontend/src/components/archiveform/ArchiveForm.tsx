import {
  Form,
  FormValidator,
  Option,
  useAlert,
  validateForm,
} from "@maykin-ui/admin-ui";
import { string2Title } from "@maykin-ui/client-common";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Afleidingswijze,
  ArchiveMeta,
  BrondatumFieldValues,
  getArchiveMetaBySelectielijstResultaatURL,
  getBrondatumFieldsByAfleidingsWijze,
} from "~/lib/resultaattype";
import { components } from "~/types";

/**
 * Props for the ArchiveForm component.
 */
export type ArchiveFormProps = {
  /** The resultaattype to set archiving options for. */
  resultaatType: components["schemas"]["ResultaatTypeWithUUID"];

  /** `Option[]` for the selectielijstklasse (resultaat) options. */
  selectielijstklasseOptions: Option[];

  /** Get called when the operation is cancelled. */
  onCancel: (reason?: string) => void;

  /** Gets called when the form is submitted. */
  onSubmit: (data: {
    selectielijstklasse: ArchiveFormData["selectielijstklasse"];
    brondatumArchiefProcedure: BrondatumFieldValues;
  }) => void;
};

export type ArchiveFormData = BrondatumFieldValues & {
  selectielijstklasse: string;
};

/**
 * Displays a dynamic form for configuring archive metadata based on
 * a `selectielijstklasse` (selectielijst result type).
 *
 * - Fetches archiving metadata using {@link getArchiveMetaBySelectielijstResultaatURL}.
 * - Dynamically constructs fields based on the selected `Afleidingswijze`.
 * - Validates inputs using the `validateForm` helper from `@maykin-ui/admin-ui`.
 */
export function ArchiveForm({
  resultaatType,
  selectielijstklasseOptions,
  onCancel,
  onSubmit,
}: ArchiveFormProps) {
  const alert = useAlert();

  /** Archive metadata from selectielijst klasse (waardering + afleidingswijzen). */
  const [archiveMeta, setArchiveMeta] = useState<ArchiveMeta | null>(null);

  /** Form field values. */
  const [formState, setFormState] = useState<ArchiveFormData>(() => {
    const resultaatTypeBrondDatumValues =
      resultaatType.brondatumArchiefprocedure || {};
    return {
      selectielijstklasse: resultaatType.selectielijstklasse,
      afleidingswijze: "afgehandeld",
      datumkenmerk: "",
      einddatumBekend: false,
      objecttype: "",
      registratie: "",
      procestermijn: "",
      ...resultaatTypeBrondDatumValues,
    };
  });

  // Fetch archive metadata on mount or when selectielijstklasse changes.
  useEffect(() => {
    const [promise, abortController] =
      getArchiveMetaBySelectielijstResultaatURL(
        resultaatType.selectielijstklasse,
      );

    promise
      .then((result) => setArchiveMeta(result))
      .catch((error) => {
        if (error.name !== "AbortError") {
          console.error("Failed to fetch archive metadata:", error);
          alert("Foutmelding", error.message, "Ok");
          onCancel(error.message);
        }
      });

    return () => abortController.abort();
  }, [formState?.selectielijstklasse || resultaatType.selectielijstklasse]);

  // Deconstruct metadata.
  const [, afleidingswijzen] = archiveMeta || [];

  // Dynamically build form fields.
  const fields = useMemo(() => {
    const bronDatumFields = formState?.afleidingswijze
      ? getBrondatumFieldsByAfleidingsWijze(
          formState.afleidingswijze as Afleidingswijze,
          { ...formState, einddatumBekend: true },
        )
      : [];

    return [
      {
        label: "Selectielijstklasse",
        name: "selectielijstklasse",
        type: "text",
        options: selectielijstklasseOptions,
        value:
          formState?.selectielijstklasse || resultaatType.selectielijstklasse,
      },
      {
        label: "Afleidingswijze",
        name: "afleidingswijze",
        type: "text",
        required: true,
        options: afleidingswijzen?.map((afleidingwijze) => ({
          label: string2Title(afleidingwijze),
          value: afleidingwijze,
          selected: formState?.afleidingswijze === afleidingwijze,
        })),
      },
      ...bronDatumFields,
    ];
  }, [formState, afleidingswijzen]);

  // Validation handler.
  const handleValidate = useCallback<FormValidator>(
    (data, fields, validators) => {
      setFormState(data as ArchiveFormData);
      return validateForm(data, fields, validators);
    },
    [],
  );

  return (
    <Form<ArchiveFormData>
      fields={fields}
      justify="stretch"
      labelSubmit="Doorgaan"
      useTypedResults
      values={formState}
      validate={handleValidate}
      validateOnChange
      onSubmit={(_, data) =>
        onSubmit({
          selectielijstklasse: data.selectielijstklasse,
          brondatumArchiefProcedure: {
            afleidingswijze: data.afleidingswijze || "",
            datumkenmerk: data.datumkenmerk || "",
            einddatumBekend: false,
            objecttype: data.objecttype || "",
            registratie: data.registratie || "",
            procestermijn: data.procestermijn || "",
          },
        })
      }
    />
  );
}

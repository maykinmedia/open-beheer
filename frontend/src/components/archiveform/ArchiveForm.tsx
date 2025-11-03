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
  /** The ZaakType. */
  zaaktype: components["schemas"]["ExpandableZaakType"];

  /** The resultaattype to set archiving options for. */
  resultaatType: components["schemas"]["ResultaatTypeWithUUID"];

  /** `Option[]` for the resultaattypeomschrijving options. */
  resultaattypeomschrijvingOptions: Option[];

  /** `Option[]` for the selectielijstklasse (resultaat) options. */
  selectielijstklasseOptions: Option[];

  /** Get called when the operation is cancelled. */
  onCancel: (reason?: string) => void;

  /** Gets called when the form is submitted. */
  onSubmit: (data: {
    omschrijving: string;
    resultaattypeomschrijving: ArchiveFormData["resultaattypeomschrijving"];
    selectielijstklasse: ArchiveFormData["selectielijstklasse"];
    brondatumArchiefprocedure: BrondatumFieldValues;
  }) => void;
};

export type ArchiveFormData = BrondatumFieldValues & {
  omschrijving: string;
  resultaattypeomschrijving: string;
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
  zaaktype,
  resultaatType,
  resultaattypeomschrijvingOptions,
  selectielijstklasseOptions,
  onCancel,
  onSubmit,
}: ArchiveFormProps) {
  const alert = useAlert();

  /** Archive metadata from selectielijst klasse (waardering + afleidingswijzen). */
  const [archiveMeta, setArchiveMeta] = useState<ArchiveMeta | null>(null);

  /** Form field values. */
  const [formState, setFormState] = useState<ArchiveFormData>({
    omschrijving: resultaatType.omschrijving,
    resultaattypeomschrijving:
      resultaatType.resultaattypeomschrijving ||
      resultaattypeomschrijvingOptions?.[0].value?.toString() ||
      "",

    selectielijstklasse:
      resultaatType.selectielijstklasse ||
      selectielijstklasseOptions?.[0]?.value?.toString() ||
      "",

    afleidingswijze:
      resultaatType.brondatumArchiefprocedure?.afleidingswijze ?? "afgehandeld",
    datumkenmerk: "",
    einddatumBekend: false,
    objecttype: "",
    registratie: "",
    procestermijn: "",
    ...Object.fromEntries(
      Object.entries(resultaatType.brondatumArchiefprocedure || {}).map(
        ([key, value]) => [key, value || ""],
      ),
    ),
  });

  // Fetch archive metadata on mount or when selectielijstklasse changes.
  useEffect(() => {
    const selectielijstklasse =
      formState?.selectielijstklasse || resultaatType.selectielijstklasse;

    const [promise, abortController] =
      getArchiveMetaBySelectielijstResultaatURL(selectielijstklasse);

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
  }, [formState, resultaatType]);

  // Deconstruct metadata.
  const [, afleidingswijzen] = archiveMeta || [];

  // Dynamically build form fields.
  const fields = useMemo(() => {
    const afleidingswijze: Afleidingswijze =
      formState.afleidingswijze || afleidingswijzen?.[0];

    const bronDatumFields = afleidingswijze
      ? getBrondatumFieldsByAfleidingsWijze(
          afleidingswijze,
          { ...formState, einddatumBekend: true },
          zaaktype,
        )
      : [];

    return [
      {
        label: "Omschrijving",
        name: "omschrijving",
        type: "text",
        value: formState?.omschrijving,
      },
      {
        label: "Resultaattypeomschrijving",
        name: "resultaattypeomschrijving",
        type: "text",
        options: resultaattypeomschrijvingOptions,
        value: formState?.resultaattypeomschrijving,
      },
      {
        label: "Selectielijstklasse",
        name: "selectielijstklasse",
        type: "text",
        options: selectielijstklasseOptions,
        value: formState?.selectielijstklasse,
      },
      {
        label: "Afleidingswijze",
        name: "afleidingswijze",
        type: "text",
        required: true,
        options: afleidingswijzen?.map((afleidingwijze) => ({
          label: string2Title(afleidingwijze),
          value: afleidingwijze,
        })),
        value: formState?.afleidingswijze || afleidingswijzen?.[0],
      },
      ...bronDatumFields,
    ];
  }, [formState, afleidingswijzen, resultaatType]);

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
          omschrijving: data.omschrijving,
          resultaattypeomschrijving: data.resultaattypeomschrijving,
          selectielijstklasse: data.selectielijstklasse,
          brondatumArchiefprocedure: {
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

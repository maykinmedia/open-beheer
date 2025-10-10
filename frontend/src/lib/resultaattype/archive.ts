import { FormField } from "@maykin-ui/admin-ui";
import { string2Title } from "@maykin-ui/client-common";
import { components } from "~/types";
import { components as selectielijstComponents } from "~/types/selectielijst";

//
// Types.
//

/**
 * A selectielijstklasse (resultaat).
 */
type Resultaat = selectielijstComponents["schemas"]["Resultaat"];

/**
 * Also known as "archiefnominatie", specified on the selectielijstklasse (resultaat).
 */
type Waardering = selectielijstComponents["schemas"]["Resultaat"]["waardering"];

/**
 * This specifies the duration of the process, it's value is used to compute the
 * available `AfleidingsWijze` values for a resultaattype.
 */
type Procestermijn =
  selectielijstComponents["schemas"]["Resultaat"]["procestermijn"];

/**
 * (Partially) describing how the brondatum for the archiving action  should be
 * computed. This is used to resolve the applicable `BrondatumField[]`.
 */
export type Afleidingswijze = components["schemas"]["AfleidingswijzeEnum"];

/**
 * Fields applicable for computing the brondatum for achiving action.
 */
export type BrondatumFieldName =
  keyof components["schemas"]["BrondatumArchiefprocedure"];

/**
 * Tuple containing both `Waardering` (archiefnominatie) and `AfleidingsWijze[]`
 * options.
 */
export type ArchiveMeta = [Waardering, Afleidingswijze[]];

//
// Public API.
//

/**
 * Fetches a {@link selectielijstComponents.schemas.Resultaat} resource from
 * the given URL and returns a tuple containing the archiefnominatie
 * (`Waardering`) and the corresponding {@link Afleidingswijze} values.
 *
 * This function returns a tuple where the first element is a Promise that
 * resolves to a 2-element tuple:
 * 1. The {@link Waardering} ("blijvend_bewaren" | "vernietigen") of the fetched result.
 * 2. An array of {@link Afleidingswijze} values derived from the result's `procestermijn`.
 *
 * The second element of the returned tuple is an {@link AbortSignal} that can be
 * used to cancel the fetch request.
 *
 * @param url - The URL pointing to a selectielijst result resource.
 *
 * @returns A tuple:
 *  - A Promise resolving to `[Waardering, AfleidingsWijze[]]`.
 *  - An {@link AbortSignal} to cancel the fetch request if needed.
 *
 * @throws Error if the fetch fails or the response is not OK.
 * @throws Error if the `procestermijn` in the result is unrecognized.
 */
export function getArchiveMetaBySelectielijstResultaatURL(
  url: string | undefined,
): [Promise<ArchiveMeta>, AbortController] {
  // If no URL is available, return some defaults.
  if (!url) {
    return [
      new Promise((resolve) => resolve(["blijvend_bewaren", ["afgehandeld"]])),
      new AbortController(),
    ];
  }
  const abortController = new AbortController();
  const promise = fetch(url, { signal: abortController.signal }).then(
    async (response) => {
      // Catch error.
      if (!response.ok) {
        throw new Error(`Failed to fetch result from URL: ${url}`);
      }

      // Get Resultaat object.
      const resultaat = (await response.json()) as Resultaat;

      // Return tuple
      return [
        resultaat.waardering as Waardering,
        getAfleidingsWijzenBySelectielijstResultaat(resultaat),
      ] as ArchiveMeta;
    },
  );

  return [promise, abortController];
}

/**
 * Form values for BrondatumFieldName fields
 * FIXME: Can't use here as the schema seems to be incorrect and `null` values
 *  are not accepted (https://github.com/open-zaak/open-zaak/issues/2206)
 */
export type BrondatumFieldValues = Omit<
  Record<BrondatumFieldName, string>,
  "einddatumBekend"
> & { einddatumBekend: boolean };

/**
 * Returns the required {@link FormField}s for computing the brondatum
 * based on a given {@link Afleidingswijze}.
 *
 * @param afleidingswijze - The derivation method.
 * @param values - The form values.
 *
 * @returns An array of {@link FormField}s required to compute the brondatum.
 */
export function getBrondatumFieldsByAfleidingsWijze(
  afleidingswijze: Afleidingswijze,
  values: BrondatumFieldValues,
): FormField[] {
  return getBrondatumFieldNamesByAfleidingsWijze(afleidingswijze).map(
    (fieldName) => getBrondatumFieldByName(fieldName, values),
  );
}

//
// Private API.
//

/**
 * Returns the {@link Afleidingswijze} values that correspond to the
 * {@link Procestermijn} of a given selectielijst result.
 *
 * This function extracts the `procestermijn` property from the provided
 * {@link selectielijstComponents.schemas.Resultaat} object and delegates
 * the lookup to {@link getAfleidingsWijzenByProcestermijn}.
 *
 * @param resultaat - The selectielijst result containing a `procestermijn`
 * property.
 *
 * @returns An array of {@link Afleidingswijze} values associated with the
 * `procestermijn` of the given result.
 *
 * @throws Error if an unrecognized process term value is provided.
 */
function getAfleidingsWijzenBySelectielijstResultaat(
  resultaat: Resultaat,
): Afleidingswijze[] {
  return getAfleidingsWijzenByProcestermijn(resultaat.procestermijn);
}

/**
 * Returns the set of possible {@link Afleidingswijze} (derivation methods)
 * that correspond to a given {@link Procestermijn} (process term).
 *
 * Each {@link Procestermijn} value maps to one or more specific
 * derivation methods used for determining record retention or processing logic.
 *
 * @param procesTermijn - The process term used to determine which
 * {@link Afleidingswijze} values apply.
 *
 * @returns An array of {@link Afleidingswijze} values that are valid for
 * the provided {@link Procestermijn}. If the term is not recognized,
 * an invariant error is thrown and an empty array is returned as a fallback.
 *
 * @throws Error if an unrecognized process term value is provided.
 */
function getAfleidingsWijzenByProcestermijn(
  procesTermijn: Procestermijn,
): Afleidingswijze[] {
  switch (procesTermijn) {
    // @ts-expect-error - FIXME: This should not happen but seems to occur in:
    // {@link https://selectielijst.openzaak.nl/api/v1/resultaten/8af64c99-a168-40dd-8afd-9fbe0597b6dc}
    case "":
    case "nihil":
      return ["afgehandeld"];

    case "bestaansduur_procesobject":
    case "vast_te_leggen_datum":
    case "samengevoegd_met_bewaartermijn":
      return [
        "ander_datumkenmerk",
        "eigenschap",
        "gerelateerde_zaak",
        "hoofdzaak",
        "ingangsdatum_besluit",
        "vervaldatum_besluit",
        "zaakobject",
      ];

    case "ingeschatte_bestaansduur_procesobject":
      return ["termijn"];
  }

  throw new Error(
    `Unable to determine AfleidingsWijze for procestermijn: "${procesTermijn}"!`,
  );
}

/**
 * Returns the names of the required fields for computing the brondatum
 * based on a given {@link Afleidingswijze}.
 *
 * @param afleidingswijze - The derivation method.
 *
 * @returns An array of {@link BrondatumFieldName}s required to compute the brondatum.
 *
 * @throws Error if the {@link Afleidingswijze} is unrecognized.
 */
function getBrondatumFieldNamesByAfleidingsWijze(
  afleidingswijze: Afleidingswijze,
): BrondatumFieldName[] {
  switch (afleidingswijze) {
    case "afgehandeld":
    case "gerelateerde_zaak":
    case "hoofdzaak":
    case "ingangsdatum_besluit":
    case "vervaldatum_besluit":
      return [];

    case "ander_datumkenmerk":
      return ["datumkenmerk", "objecttype", "registratie"];

    case "eigenschap":
      return ["datumkenmerk"];

    case "termijn":
      return ["procestermijn"];

    case "zaakobject":
      return ["datumkenmerk", "objecttype"];
  }

  throw new Error(
    `Unable to determine BrondatumFields for afleidingswijze: "${afleidingswijze}"!`,
  );
}

/**
 * Returns a {@link FormField} configuration object for a given
 * {@link BrondatumFieldName}.
 *
 * @param brondatumFieldName - The name of the brondatum field.
 * @param values - The form values.
 *
 * @returns A {@link FormField} describing the type and options (if any)
 * required for this brondatum field.
 *
 * @throws Error if the {@link BrondatumFieldName} is unrecognized.
 */
function getBrondatumFieldByName(
  brondatumFieldName: BrondatumFieldName,
  values: BrondatumFieldValues,
): FormField {
  const value = values[brondatumFieldName];
  return {
    label: string2Title(brondatumFieldName),
    ..._getBrondatumFieldStubByName(brondatumFieldName),
    value: typeof value === "string" ? value : undefined,
    checked: typeof value === "boolean" ? value : undefined,
  };
}

function _getBrondatumFieldStubByName(
  brondatumFieldName: BrondatumFieldName,
): FormField {
  switch (brondatumFieldName) {
    case "afleidingswijze":
      return {
        name: brondatumFieldName,
        type: "text",
        required: true,
        options: [
          { label: "Afgehandeld", value: "afgehandeld" },
          { label: "Ander datumkenmerk", value: "ander_datumkenmerk" },
          { label: "Eigenschap", value: "eigenschap" },
          { label: "Gerelateerde zaak", value: "gerelateerde_zaak" },
          { label: "Hoofdzaak", value: "hoofdzaak" },
          { label: "Ingangsdatum besluit", value: "ingangsdatum_besluit" },
          { label: "Termijn", value: "termijn" },
          { label: "Vervaldatum besluit", value: "vervaldatum_besluit" },
          { label: "Zaakobject", value: "zaakobject" },
        ],
      };

    case "datumkenmerk":
    case "registratie":
    case "procestermijn":
      return {
        name: brondatumFieldName,
        type: "text",
        required: true,
      };

    case "einddatumBekend":
      return {
        name: brondatumFieldName,
        type: "checkbox",
      };

    case "objecttype":
      return {
        name: brondatumFieldName,
        type: "text",
        required: true,
        options: [
          { label: "Adres", value: "adres" },
          { label: "Besluit", value: "besluit" },
          { label: "Buurt", value: "buurt" },
          { label: "Enkelvoudig document", value: "enkelvoudig_document" },
          { label: "Gemeente", value: "gemeente" },
          {
            label: "Gemeentelijke openbare ruimte",
            value: "gemeentelijke_openbare_ruimte",
          },
          { label: "Huishouden", value: "huishouden" },
          { label: "Inrichtingselement", value: "inrichtingselement" },
          {
            label: "Kadastrale onroerende zaak",
            value: "kadastrale_onroerende_zaak",
          },
          { label: "Kunstwerkdeel", value: "kunstwerkdeel" },
          {
            label: "Maatschappelijke activiteit",
            value: "maatschappelijke_activiteit",
          },
          { label: "Medewerker", value: "medewerker" },
          { label: "Natuurlijk persoon", value: "natuurlijk_persoon" },
          {
            label: "Niet-natuurlijk persoon",
            value: "niet_natuurlijk_persoon",
          },
          { label: "Openbare ruimte", value: "openbare_ruimte" },
          {
            label: "Organisatorische eenheid",
            value: "organisatorische_eenheid",
          },
          { label: "Pand", value: "pand" },
          { label: "Spoorbaandeel", value: "spoorbaandeel" },
          { label: "Status", value: "status" },
          { label: "Terreindeel", value: "terreindeel" },
          { label: "Terrein gebouwd object", value: "terrein_gebouwd_object" },
          { label: "Vestiging", value: "vestiging" },
          { label: "Waterdeel", value: "waterdeel" },
          { label: "Wegdeel", value: "wegdeel" },
          { label: "Wijk", value: "wijk" },
          { label: "Woonplaats", value: "woonplaats" },
          { label: "Woz deel object", value: "woz_deelobject" },
          { label: "Woz object", value: "woz_object" },
          { label: "Woz waarde", value: "woz_waarde" },
          { label: "Zakelijk recht", value: "zakelijk_recht" },
          { label: "Overige", value: "overige" },
        ],
      };
  }

  throw new Error(
    `Unable to build FormField for brondatumFieldName: "${brondatumFieldName}"!`,
  );
}

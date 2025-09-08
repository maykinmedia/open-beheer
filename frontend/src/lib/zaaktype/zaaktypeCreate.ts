import { FormField } from "@maykin-ui/admin-ui";

export const ZAAKTYPE_CREATE_BASE_FIELDS: FormField[] = [
  {
    label: "Identificatienummer",
    name: "identificatie",
    type: "text",
    required: true,
  },
  {
    label: "Omschrijving",
    name: "omschrijvingGeneriek",
    type: "text",
    required: true,
  },
];

export type DefaultValues<
  T extends FormField[] = typeof ZAAKTYPE_CREATE_BASE_FIELDS,
> = Record<Exclude<T[number]["name"], undefined>, unknown>;

export function getZaaktypeCreateFields(
  defaultValues: DefaultValues = {},
): FormField[] {
  return ZAAKTYPE_CREATE_BASE_FIELDS.map((f) => {
    if ("defaultValue" in f && f.name) {
      f.defaultValue = String(defaultValues[f.name] || f.defaultValue);
    }
    return f;
  });
}

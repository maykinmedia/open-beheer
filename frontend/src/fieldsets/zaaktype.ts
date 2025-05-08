import { FieldSet } from "@maykin-ui/admin-ui";
import { ZaakType } from "~/types";

export const ZAAKTYPE_FIELDSETS: FieldSet<ZaakType>[] = [
  [
    "Algemeen",
    {
      fields: ["identificatie", "uuid", "omschrijving", "url"],
      title: "identificatie",
      span: 12,
    },
  ],
];

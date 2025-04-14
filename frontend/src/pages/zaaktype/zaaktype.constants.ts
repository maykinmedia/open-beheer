import { FieldSet } from "@maykin-ui/admin-ui";
import { ZaakType } from "~/pages";

export const ZAAKTYPE_FIELDSETS: FieldSet<ZaakType>[] = [
  [
    "Algemeen",
    {
      fields: ["id", "name", "age"],
      title: "name",
      span: 12,
    },
  ],
  [
    "Contact",
    {
      fields: ["email"],
      span: 12,
    },
  ],
];

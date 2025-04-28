import { FieldSet } from "@maykin-ui/admin-ui";
import { ZaakType } from "~/types";

export const ZAAKTYPE_FIELDSETS: FieldSet<ZaakType>[] = [
  [
    "Algemeen",
    {
      fields: [
        "identificatie",
        "omschrijving",
        // "broncatalogus",
        "verantwoordelijke",
      ],
      title: "identificatie",
      span: 12,
    },
  ],
  [
    "Geldigheid",
    {
      fields: [
        "datumBeginGeldigheid",
        "datumEindeGeldigheid",
        "publicatieIndicatie",
      ],
      span: 12,
    },
  ],
];

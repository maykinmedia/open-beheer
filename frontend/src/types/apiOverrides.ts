/**
 * This file overrides auto-generated api.d.ts, fixing issues in created type.
 */
import { components as generatedComponents } from "~/types/api";

// https://github.com/open-zaak/open-zaak/issues/2085
type ZaakType = Omit<
  generatedComponents["schemas"]["ExpandableZaakType"],
  "url"
> & {
  url: string;
};

// https://github.com/maykinmedia/open-beheer/issues/94
type User = Omit<
  generatedComponents["schemas"]["User"],
  "first_name" | "last_name"
> & {
  firstName: generatedComponents["schemas"]["User"]["firstName"];
  lastName: generatedComponents["schemas"]["User"]["lastName"];
};

export type components = Omit<generatedComponents, "schemas"> & {
  schemas: Omit<generatedComponents["schemas"], "ZaakType"> & {
    User: User;
    ZaakType: ZaakType;
  };
};

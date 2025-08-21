/**
 * This file overrides auto-generated api.d.ts, fixing issues in created type.
 */
import { components as generatedComponents } from "~/types/api";

type ExpandableZaakType = Omit<
  generatedComponents["schemas"]["ExpandableZaakType"],
  "url"
> & {
  url: string;
};

type DetailResponse_ExpandableZaakType_ = Omit<
  generatedComponents["schemas"]["DetailResponse_ExpandableZaakType_"],
  "result"
> & {
  result: ExpandableZaakType;
};

export type components = Omit<generatedComponents, "schemas"> & {
  schemas: Omit<generatedComponents["schemas"], "ZaakType"> & {
    ExpandableZaakType: ExpandableZaakType;
    DetailResponse_ExpandableZaakType_: DetailResponse_ExpandableZaakType_;
  };
};

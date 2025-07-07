/**
 * This file overrides auto-generated api.d.ts, fixing issues in created type.
 */
import { components as generatedComponents } from "~/types/api";

// https://github.com/open-zaak/open-zaak/issues/2085
type ZaakType = Omit<generatedComponents["schemas"]["ZaakType"], "url"> & {
  url: string;
};
type DetailResponse_ZaakType_ = Omit<
  generatedComponents["schemas"]["DetailResponse_ZaakType_"],
  "result"
> & {
  result: ZaakType;
};

export type components = Omit<generatedComponents, "schemas"> & {
  schemas: Omit<generatedComponents["schemas"], "ZaakType"> & {
    ZaakType: ZaakType;
    DetailResponse_ZaakType_: DetailResponse_ZaakType_;
  };
};

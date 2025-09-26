import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_RESULTAATTYPEN: TabConfig<TargetType> = {
  label: "Resultaattypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        "_expand.resultaattypen.omschrijving",
        // See https://vng-realisatie.github.io/gemma-zaken/standaard/catalogi/#ztc-002
        // omschrijvingGeneriek == label of resultaattypeomschrijving
        "_expand.resultaattypen.resultaattypeomschrijving",
        "_expand.resultaattypen.selectielijstklasse",
        "_expand.resultaattypen.uuid",
      ],
      label: "Resultaattypen",
      key: "resultaattypen",
    },
  ],
};

import { TabConfig, TargetType } from "~/pages";

export const TABS_CONFIG_ROLTYPEN: TabConfig<TargetType> = {
  label: "Roltypen",
  view: "DataGrid",
  sections: [
    {
      expandFields: [
        "omschrijving",
        {
          name: "omschrijvingGeneriek",
          type: "string",
          options: [
            { label: "Adviseur", value: "adviseur" },
            { label: "Behandelaar", value: "behandelaar" },
            { label: "Belanghebbende", value: "belanghebbende" },
            { label: "Beslisser", value: "beslisser" },
            { label: "Klantcontacter", value: "klantcontacter" },
            { label: "Medeinitiator", value: "mede_initiator" },
            { label: "Zaakcoordinator", value: "zaakcoordinator" },
          ],
        },
      ],
      label: "Roltypen",
      key: "roltypen",
    },
  ],
};

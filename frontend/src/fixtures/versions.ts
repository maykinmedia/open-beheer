import { components } from "~/types";

export const FIXTURE_ZAAKTYPE_VERSIONS: components["schemas"]["VersionSummary"][] =
  [
    {
      uuid: "09d7c3b6-153e-4bcf-b8cd-55c11ffd2c76",
      concept: false,
      beginGeldigheid: "2022-01-01",
      eindeGeldigheid: "2022-12-31",
    },
    {
      uuid: "08370480-e843-4d9c-aced-56ddb8595d22",
      concept: false,
      beginGeldigheid: "2023-01-01",
      eindeGeldigheid: "2023-12-31",
    },
    {
      uuid: "0dd7a5ca-9c49-4750-a063-616ed00040e6",
      concept: false,
      beginGeldigheid: "2024-01-01",
      eindeGeldigheid: "2024-12-31",
    },
    {
      uuid: "fc685de7-d386-4d9f-861c-244700d68e80",
      concept: false,
      beginGeldigheid: "2025-01-01",
      eindeGeldigheid: "2025-12-31",
    },
    {
      uuid: "37454e74-99cd-4689-9589-c819ad8f1b88",
      concept: true,
      beginGeldigheid: "2025-08-01",
      eindeGeldigheid: null,
    },
  ];

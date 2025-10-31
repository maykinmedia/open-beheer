import { request } from "~/api/request.ts";
import { ListResponse } from "~/api/types";
import { components } from "~/types";

export const getZaaktype = async ({
  serviceSlug,
  catalogusId,
  identificatie,
  omschrijving,
}: {
  serviceSlug: string;
  catalogusId: string;
  identificatie?: string;
  omschrijving?: string;
}) => {
  const response = await request<
    ListResponse<components["schemas"]["ZaakTypeSummary"]>
  >("GET", `/service/${serviceSlug}/zaaktypen/`, {
    catalogus: catalogusId,
    identificatie__icontains: identificatie,
    omschrijving__icontains: omschrijving,
  });
  return { ...response };
};

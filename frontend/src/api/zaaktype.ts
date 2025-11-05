import { request } from "~/api/request.ts";
import { ListResponse } from "~/api/types";
import { components } from "~/types";

export const getZaaktype = async ({
  serviceSlug,
  zaaktypeUUID,
}: {
  serviceSlug: string;
  zaaktypeUUID: string;
}) => {
  const response = await request<
    components["schemas"]["DetailResponse_ExpandableZaakType_"]
  >("GET", `/service/${serviceSlug}/zaaktypen/${zaaktypeUUID}/`);
  return { ...response };
};

/**
 * Fetches "Zaaktype" from a given service catalog.
 *
 * @param serviceSlug - The identifier of the service to query.
 * @param catalogusId - The ID of the catalog to filter by.
 * @param identificatie - Optional partial match filter for the identification field.
 * @param omschrijving - Optional partial match filter for the description field.
 * @returns A promise resolving to a list response containing ZaakTypeSummary objects.
 */
export const getZaaktypen = async ({
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
  const params = new URLSearchParams();
  params.set("catalogus", catalogusId);
  if (identificatie) {
    params.set("identificatie__icontains", identificatie);
  }
  if (omschrijving) {
    params.set("omschrijving__icontains", omschrijving);
  }

  const response = await request<
    ListResponse<components["schemas"]["ZaakTypeSummary"]>
  >("GET", `/service/${serviceSlug}/zaaktypen/`, params);
  return { ...response };
};

// TODO: Get from GEMMA dynamically
export type ZaakType = {
  url: string;
  identificatie: string; // e.g. "ZAAKTYPE-123"
  omschrijving: string; // Short description
  doel: string; // Purpose of the case type
  verantwoordelijke: string; // Responsible organization or role
  publicatieIndicatie: boolean;
  datumBeginGeldigheid: string; // ISO date string (e.g. "2024-01-01")
  datumEindeGeldigheid: string | null; // ISO date or null
  zaakcategorie: string | null;
  broncatalogus: string; // URL to the catalog resource
};

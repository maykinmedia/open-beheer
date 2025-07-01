export type ZaakType = {
  uuid: string; // Added by BFF.

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

export type ZaakTypeVersion = {
  uuid: string; // Unique identifier for the version
  beginGeldigheid: string; // ISO date string (e.g. "2024-01-01")
  eindeGeldigheid: string | null; // ISO date or null
  concept: boolean | null; // Indicates if this is a concept version
};

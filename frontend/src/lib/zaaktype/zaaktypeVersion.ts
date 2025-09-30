import { components } from "~/types";

/**
 * Sorts a list of `VersionSummary` objects by their `beginGeldigheid` date
 * in ascending order (earliest first).
 *
 * @param versions - Array of version summaries to sort.
 * @returns A new array of `VersionSummary` objects sorted by start date.
 */
export function sortZaaktypeVersions(
  versions: components["schemas"]["VersionSummary"][],
): components["schemas"]["VersionSummary"][] {
  return versions.sort(
    (a, b) =>
      new Date(a.beginGeldigheid).getTime() -
      new Date(b.beginGeldigheid).getTime(),
  );
}

/**
 * Finds the currently active (non-concept) `VersionSummary` from a list of versions.
 * A version is considered active if:
 * - it is not a concept (`!v.concept`)
 * - its `beginGeldigheid` is today or earlier
 * - its `eindeGeldigheid` is not set, or is later than today
 *
 * @param versions - Array of version summaries to search.
 * @returns The active `VersionSummary` if found, otherwise `undefined`.
 */
export function findActiveZaaktypeVersion(
  versions: components["schemas"]["VersionSummary"][],
): components["schemas"]["VersionSummary"] | undefined {
  const today = new Date();
  return versions.find((v) => {
    const beginDate = new Date(v.beginGeldigheid);
    const endDate = v.eindeGeldigheid ? new Date(v.eindeGeldigheid) : null;

    return !v.concept && beginDate <= today && (!endDate || endDate > today);
  });
}

/**
 * Finds the concept (draft) `VersionSummary` from a list of versions.
 * A version is considered a concept if its `concept` flag is `true`.
 *
 * @param versions - Array of version summaries to search.
 * @returns The concept `VersionSummary` if found, otherwise `undefined`.
 */
export function findConceptZaaktypeVersion(
  versions: components["schemas"]["VersionSummary"][],
): components["schemas"]["VersionSummary"] | undefined {
  return versions.find((v) => v.concept);
}

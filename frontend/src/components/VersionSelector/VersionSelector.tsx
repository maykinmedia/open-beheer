import { Button, Outline } from "@maykin-ui/admin-ui";
import { formatDate } from "@storybook/blocks";
import { FC, useId, useMemo, useState } from "react";
import { components } from "~/types";

import "./VersionSelector.css";

interface VersionSelectorProps {
  selectedVersionUUID: string;
  versions: components["schemas"]["VersionSummary"][];
  onVersionChange?: (version: components["schemas"]["VersionSummary"]) => void;
}

/**
 * A reusable component to select a version of a ZaakType.
 *
 * @param currentVersionUUID - The UUID of the version to show.
 * @param versions - An array of versions of a ZaakType as returned by the BFF.
 * @param onVersionChange - An (optional) callback function to handle version changes.
 * @returns A section with (collapsible) buttons to select a version.
 * @example
 * ```tsx
 * <VersionSelector
 *  currentVersionUUID="1"
 *  versions={[
 *  { uuid: "1", begin_geldigheid: "2023-01-01", einde_geldigheid: null, concept: false },
 *  { uuid: "2", begin_geldigheid: "2024-01-01", einde_geldigheid: "2023-12-31", concept: false },
 *  { uuid: "3", begin_geldigheid: "2024-02-01", einde_geldigheid: null, concept: true },
 *  { uuid: "4", begin_geldigheid: "2024-03-01", einde_geldigheid: null, concept: false },
 *  ]}
 *  onVersionChange={(versionId) => console.log("Selected version:", versionId)}
 *  />
 * ```
 *  */
export const VersionSelector: FC<VersionSelectorProps> = ({
  selectedVersionUUID,
  versions,
  onVersionChange,
}) => {
  const id = useId();
  const headingId = `version-selector-heading-${id}`;
  const [isExpanded, setIsExpanded] = useState(false);

  const today = new Date();

  // Versions sorted by date.
  const sortedVersions = useMemo(
    () =>
      [...versions].sort(
        (a, b) =>
          new Date(a.beginGeldigheid).getTime() -
          new Date(b.beginGeldigheid).getTime(),
      ),
    [versions],
  );

  // The current active (but not necessarily selected) versions
  const currentVersion = useMemo(
    () =>
      sortedVersions.find((v) => {
        const beginDate = new Date(v.beginGeldigheid);
        const endDate = v.eindeGeldigheid ? new Date(v.eindeGeldigheid) : null;

        return (
          !v.concept && beginDate <= today && (!endDate || endDate > today)
        );
      }),
    [sortedVersions],
  );

  // The (last) concept version, we assume there should be max 1.
  const conceptVersion = useMemo(() => {
    const concepts = sortedVersions.filter((v) => v.concept);
    return concepts[concepts.length - 1];
  }, [sortedVersions]);

  const handleVersionChange = (
    version: components["schemas"]["VersionSummary"],
  ) => {
    onVersionChange?.(version);
  };

  // Historical versions.
  const historicalVersions = useMemo(
    () =>
      sortedVersions.filter(
        (v) =>
          !v.concept &&
          new Date(v.beginGeldigheid) < today &&
          (v.eindeGeldigheid ? new Date(v.eindeGeldigheid) <= today : false),
      ),
    [sortedVersions],
  );

  // The version to render.
  const visibleVersions = useMemo(() => {
    const fullList = [
      ...historicalVersions,
      ...(currentVersion ? [currentVersion] : []),
      ...(conceptVersion ? [conceptVersion] : []),
    ];

    if (isExpanded) {
      return fullList;
    }

    return fullList.filter((v) => {
      return (
        v.uuid === currentVersion?.uuid ||
        v.uuid === conceptVersion?.uuid ||
        v.uuid === selectedVersionUUID
      );
    });
  }, [historicalVersions, currentVersion, conceptVersion, isExpanded]);

  /**
   * Returns the label for the version.
   */
  const getVersionLabel = (
    version: components["schemas"]["VersionSummary"],
  ) => {
    const beginDate = new Date(version.beginGeldigheid);
    const endDate = version.eindeGeldigheid
      ? new Date(version.eindeGeldigheid)
      : null;

    if (version.concept) {
      return `Concept versie ${version.uuid}`;
    }

    const isCurrent = beginDate <= today && (!endDate || endDate > today);

    if (isCurrent) {
      return `Actueel`;
    }

    return `${formatDate(beginDate)}${endDate ? ` - ${formatDate(endDate)}` : ""}`;
  };

  return (
    <section className="version-selector" aria-labelledby={headingId}>
      <h3 id={headingId} className="version-selector__screenreader-only">
        Kies een versie
      </h3>

      <div
        className="version-selector__buttons"
        role="group"
        aria-label="Versiekeuze"
      >
        {historicalVersions.length > 0 && (
          <Button
            className="version-selector__toggle-button"
            variant="secondary" // TODO: Use "accent" variant when available in Maykin UI
            onClick={() => setIsExpanded((prev) => !prev)}
            aria-expanded={isExpanded}
            aria-label={
              isExpanded ? "Toon minder versies" : "Toon meer versies"
            }
          >
            {isExpanded ? (
              <>
                <Outline.MinusIcon aria-hidden="true" />
                <span>Toon minder</span>
              </>
            ) : (
              <>
                <Outline.PlusIcon aria-hidden="true" />
                <span>Toon meer</span>
              </>
            )}
          </Button>
        )}

        {visibleVersions.map((version) => {
          const versionLabel = getVersionLabel(version);
          return (
            <Button
              key={version.uuid}
              className={`version-selector__version-button ${
                selectedVersionUUID === version.uuid
                  ? "version-selector__version-button--active"
                  : ""
              }`}
              variant={
                selectedVersionUUID === version.uuid ? "primary" : "secondary"
              } // TODO: Use "accent" variant when available in Maykin UI
              onClick={() => handleVersionChange(version)}
              aria-pressed={selectedVersionUUID === version.uuid}
              aria-label={`Selecteer ${versionLabel}`} // TODO: Need a label from backend?
            >
              {/*  TODO: Need a label from backend? */}
              {versionLabel}
            </Button>
          );
        })}
      </div>
    </section>
  );
};

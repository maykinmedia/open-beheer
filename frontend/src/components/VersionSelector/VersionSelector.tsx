import { Button, Outline } from "@maykin-ui/admin-ui";
import { FC, useId, useState } from "react";
import { ZaakTypeVersion } from "~/types";

import "./VersionSelector.css";

interface VersionSelectorProps {
  versions: ZaakTypeVersion[];
  onVersionChange?: (versionId: string) => void;
}

/**
 * A reusable component to select a version of a ZaakType.
 * This component makes a few assumptions:
 * - The versions are NOT sorted, we expect the backend to provide them in the correct order.
 * - The current version is the one with a truthy `einde_geldigheid`.
 * - The concept version is the one with `concept` set to true.
 * - All other versions are considered historical versions.
 *
 * @param versions - An array of versions of a ZaakType as returned by the BFF.
 * @param onVersionChange - An (optional) callback function to handle version changes.
 * @returns A section with (collapsible) buttons to select a version.
 * @example
 * ```tsx
 * <VersionSelector
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
  versions,
  onVersionChange,
}) => {
  const id = useId();
  const headingId = `version-selector-heading-${id}`;

  const today = new Date();

  const currentVersion = versions.find((v) => {
    const beginDate = new Date(v.beginGeldigheid);
    const endDate = v.eindeGeldigheid ? new Date(v.eindeGeldigheid) : null;

    return !v.concept && beginDate <= today && (!endDate || endDate > today);
  });

  const conceptVersion = versions
    .filter((v) => v.concept)
    .sort(
      (a, b) =>
        new Date(b.beginGeldigheid).getTime() -
        new Date(a.beginGeldigheid).getTime(),
    )[0];

  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedVersionId, setSelectedVersionId] = useState<
    string | undefined
  >(currentVersion?.uuid || conceptVersion?.uuid);

  const handleVersionChange = (versionId: string) => {
    setSelectedVersionId(versionId);
    onVersionChange?.(versionId);
  };

  const getVisibleVersions = () => {
    if (isExpanded) {
      return versions;
    }

    return versions.filter((v) => {
      return (
        v.uuid === currentVersion?.uuid ||
        v.uuid === conceptVersion?.uuid ||
        v.uuid === selectedVersionId
      );
    });
  };

  const getVersionLabel = (version: ZaakTypeVersion) => {
    const beginDate = new Date(version.beginGeldigheid);
    const endDate = version.eindeGeldigheid
      ? new Date(version.eindeGeldigheid)
      : null;

    if (version.concept) {
      return `Concept versie ${version.uuid}`;
    }

    const isCurrent = beginDate <= today && (!endDate || endDate > today);

    if (isCurrent) {
      return `Huidige versie ${version.uuid}`;
    }

    return `Historische versie ${version.uuid}`;
  };

  return (
    <section className="version-selector" aria-labelledby={headingId}>
      <h2 id={headingId} className="version-selector__screenreader-only">
        Kies een versie
      </h2>

      <div
        className="version-selector__buttons"
        role="group"
        aria-label="Versiekeuze"
      >
        <Button
          className="version-selector__toggle-button"
          variant="secondary" // TODO: Use "accent" variant when available in Maykin UI
          onClick={() => setIsExpanded((prev) => !prev)}
          aria-expanded={isExpanded}
          aria-label={isExpanded ? "Toon minder versies" : "Toon meer versies"}
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

        {getVisibleVersions().map((version) => {
          const versionLabel = getVersionLabel(version);
          return (
            <Button
              key={version.uuid}
              className={`version-selector__version-button ${
                selectedVersionId === version.uuid
                  ? "version-selector__version-button--active"
                  : ""
              }`}
              variant={
                selectedVersionId === version.uuid ? "primary" : "secondary"
              } // TODO: Use "accent" variant when available in Maykin UI
              onClick={() => handleVersionChange(version.uuid)}
              aria-pressed={selectedVersionId === version.uuid}
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

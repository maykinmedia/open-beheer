import { Button, Outline, P } from "@maykin-ui/admin-ui";
import { FC, ReactNode, useState } from "react";

import "./VersionSelector.css";

type Version = {
  id: string;
  label: string;
  isCurrent?: boolean;
  isConcept?: boolean;
};

type VersionContent = {
  id: string;
  children: ReactNode;
};

interface VersionSelectorProps {
  versions: Version[];
  content: VersionContent[];
}

export const VersionSelector: FC<VersionSelectorProps> = ({
  versions,
  content,
}) => {
  const currentVersion = versions.find((v) => v.isCurrent);
  const conceptVersion = versions.find((v) => v.isConcept);

  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedVersionId, setSelectedVersionId] = useState(
    currentVersion?.id || versions[0]?.id,
  );

  const selectedContent = content.find((item) => item.id === selectedVersionId);

  const getVisibleVersions = () => {
    // If expanded, show all versions
    // If not expanded, show only the current and concept versions, and also the selected version
    if (isExpanded) {
      return versions;
    }
    return versions.filter(
      (v) =>
        v.isCurrent ||
        v.isConcept ||
        v.id === selectedVersionId ||
        v.id === currentVersion?.id ||
        v.id === conceptVersion?.id,
    );
  };

  return (
    <section
      className="version-selector"
      aria-labelledby="version-selector-heading"
    >
      <h2
        id="version-selector-heading"
        className="version-selector__screenreader-only"
      >
        Kies een versie
      </h2>

      <div
        className="version-selector__buttons"
        role="group"
        aria-label="Versiekeuze"
      >
        <Button
          className="version-selector__toggle-button"
          variant="secondary"
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

        {getVisibleVersions().map((version) => (
          <Button
            key={version.id}
            className={`version-selector__version-button ${
              selectedVersionId === version.id
                ? "version-selector__version-button--active"
                : ""
            }`}
            variant={selectedVersionId === version.id ? "primary" : "secondary"}
            onClick={() => setSelectedVersionId(version.id)}
            aria-pressed={selectedVersionId === version.id}
            aria-label={`Selecteer versie ${version.label}`}
          >
            {version.label}
          </Button>
        ))}
      </div>

      <div className="version-selector__content">
        {selectedContent?.children ?? (
          <P className="version-selector__no-content" role="status">
            Geen inhoud gevonden voor versie: {selectedVersionId}
          </P>
        )}
      </div>
    </section>
  );
};

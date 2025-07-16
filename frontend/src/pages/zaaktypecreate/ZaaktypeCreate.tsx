import {
  A,
  Body,
  Button,
  Card,
  CardBaseTemplate,
  Column,
  Grid,
  H1,
  Outline,
  P,
  Ul,
} from "@maykin-ui/admin-ui";
import React from "react";
import { useLoaderData } from "react-router";
import { useBreadcrumbItems } from "~/hooks";
import { ZaaktypeCreateLoaderData } from "~/pages";

import "./zaaktypeCreate.styles.css";

/**
 * TODO:
 * - We need more Padding inside of the Card component.
 * - Card is for some reason a checkbox not radio? Maykin ui bug?
 */

export function ZaaktypeCreatePage() {
  const { results } = useLoaderData<ZaaktypeCreateLoaderData>();
  const breadcrumbItems = useBreadcrumbItems();
  const [selectedTemplate, setSelectedTemplate] = React.useState<string | null>(
    null,
  );

  const handleSubmit = () => {
    // TODO: Implement the submit logic to create a new zaaktype based on the selected template.
  };

  return (
    <CardBaseTemplate breadcrumbItems={breadcrumbItems}>
      <Body>
        <Grid fullHeight={true}>
          <Column span={12}>
            <H1>Kies een sjabloon</H1>
          </Column>
          <Column span={6}>
            <P>
              Maak een nieuw zaaktype aan door te starten vanaf een sjabloon of
              met een blanco opzet. Kies de variant die het beste past bij het
              soort proces dat je wilt inrichten
            </P>
          </Column>
          <Column span={6} />

          {results.map((result) => (
            <Column
              span={3}
              key={result.uuid}
              className="zaaktypecreate__card-column-wrapper"
            >
              <ZaaktypeCreateCard
                result={result}
                selectedTemplate={selectedTemplate}
                setSelectedTemplate={setSelectedTemplate}
              />
            </Column>
          ))}
          <Column span={12}>
            <Button
              variant="secondary"
              disabled={!selectedTemplate}
              onClick={handleSubmit}
            >
              Gebruik dit sjabloon
            </Button>
            <P>
              Of kopieer een <A href="/zaaktypen">bestaand zaaktype</A>
            </P>
          </Column>
        </Grid>
      </Body>
    </CardBaseTemplate>
  );
}

type ZaaktypeCreateCardProps = {
  result: ZaaktypeCreateLoaderData["results"][number];
  selectedTemplate: string | null;
  setSelectedTemplate: (uuid: string | null) => void;
};

export const ZaaktypeCreateCard: React.FC<ZaaktypeCreateCardProps> = ({
  result,
  selectedTemplate,
  setSelectedTemplate,
}) => {
  return (
    <Card
      className="zaaktypecreate__card"
      onClick={() => setSelectedTemplate(result.uuid || null)}
      border={true}
      title={result.naam}
      actions={[
        {
          type: "radio",
          name: `zaaktypecreate-${result.naam}`,
          value: result.uuid,
          checked: selectedTemplate === result.uuid,
        },
      ]}
    >
      <Body fullHeight={true} className="zaaktypecreate__card-body">
        <P>{result.omschrijving}</P>
        {result.voorbeelden.length > 0 && (
          <Ul>
            {result.voorbeelden.map((voorbeeld) => (
              <li key={voorbeeld}>{voorbeeld}</li>
            ))}
          </Ul>
        )}
        <div className="zaaktypecreate__link">
          <A href={``}>
            <Outline.EyeIcon /> Bekijk voorbeeld
          </A>
        </div>
      </Body>
    </Card>
  );
};

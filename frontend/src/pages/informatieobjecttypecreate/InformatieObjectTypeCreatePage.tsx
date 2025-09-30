import {
  Body,
  Button,
  Card,
  CardBaseTemplate,
  Column,
  Form,
  FormField,
  Grid,
  H1,
  H2,
  Modal,
  P,
} from "@maykin-ui/admin-ui";
import { FormEvent, useContext, useState } from "react";
import { useParams } from "react-router";
import { CATALOGUS_PARAM, OBContext } from "~/App.tsx";
import { useBreadcrumbItems } from "~/hooks";
import { useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import { getUUIDFromString } from "~/lib/format/string";

import {
  InformatieObjectTypeCreateAction,
  InformatieObjectTypeCreateActionPayload,
} from "./informatieobjecttype.action";

export const INFORMATIEOBJECTTYPE_CREATE_BASE_FIELDS: FormField[] = [
  {
    label: "Omschrijving",
    name: "omschrijving",
    type: "text",
    required: true,
  },
];

type TemplateInformatieObjectTypeData = {
  omschrijving: string;
};

export function InformatieObjectTypeCreatePage() {
  const obContext = useContext(OBContext);
  const params = useParams();
  const submitAction = useSubmitAction<InformatieObjectTypeCreateAction>(false);
  const breadcrumbItems = useBreadcrumbItems();
  const [isModalOpen, setModalOpen] = useState<boolean>(false);
  const [errors, setErrors] = useState<string[] | undefined>();

  const catalogusUrl = obContext.catalogiChoices.find(
    (c) => getUUIDFromString(c.value) === params[CATALOGUS_PARAM],
  )?.value;

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
    data: TemplateInformatieObjectTypeData,
  ) => {
    event.preventDefault();

    if (!catalogusUrl) {
      setErrors(["Could not find catalogus URL."]); // This should™ never happen
      return;
    }

    const today = new Date();
    // @ts-expect-error: FIXME - the backend types say that these fields should be present and null, while they can be absent.
    const requestPayload: InformatieObjectTypeCreateActionPayload = {
      vertrouwelijkheidaanduiding: "openbaar",
      omschrijving: data.omschrijving,
      catalogus: catalogusUrl,
      beginGeldigheid: today.toISOString().substring(0, 10),
      informatieobjectcategorie: "Een categorie",
    };

    await submitAction({
      type: "INFORMATIEOBJECTTYPE_CREATE",
      payload: requestPayload,
    });
  };

  return (
    <CardBaseTemplate breadcrumbItems={breadcrumbItems}>
      <Modal
        size="m"
        title={`Sjabloon default`}
        open={isModalOpen}
        onClose={() => setModalOpen(false)}
      >
        <Body fullHeight>
          <P>
            Je staat op het punt een nieuw informatieobjecttype te starten. Vul
            deze velden in.
          </P>
          <Form
            key={`informatieobjecttype-form`}
            aria-label="Informatieobjecttype aanmaken"
            nonFieldErrors={errors}
            fields={INFORMATIEOBJECTTYPE_CREATE_BASE_FIELDS}
            justify="stretch"
            validateOnChange
            showActions={true}
            onSubmit={handleSubmit}
          />
        </Body>
      </Modal>
      <Body>
        <Grid fullHeight={true}>
          <Column span={12}>
            <H1>Kies een sjabloon</H1>
          </Column>
          <Column span={6}>
            <P>
              Maak een nieuw informatieobjecttype aan door te starten vanaf een
              sjabloon of met een blanco opzet. Kies de variant die het beste
              past bij het soort proces dat je wilt inrichten
            </P>
          </Column>
          <Column span={6} />

          <Card
            className="zaaktypecreate__card"
            border={true}
            titleAs={H2}
            title="Default"
          >
            <Body fullHeight={true} className="zaaktypecreate__card-body">
              <P>Een default informatieobjecttype</P>
            </Body>
          </Card>
          <Column span={12}>
            <Button variant="primary" onClick={() => setModalOpen(true)}>
              Gebruik dit sjabloon
            </Button>
          </Column>
        </Grid>
      </Body>
    </CardBaseTemplate>
  );
}

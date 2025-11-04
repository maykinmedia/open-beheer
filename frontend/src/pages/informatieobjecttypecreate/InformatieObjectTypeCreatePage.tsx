import { FormField } from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import { FormEvent, useContext } from "react";
import { useParams } from "react-router";
import { CATALOGUS_PARAM, OBContext } from "~/App.tsx";
import { useSubmitAction } from "~/hooks/useSubmitAction.tsx";
import { getUUIDFromString } from "~/lib/format/string";
import {
  InformatieObjectTypeCreateAction,
  InformatieObjectTypeCreateActionPayload,
} from "~/pages";
import { CreateView, TemplateBase } from "~/views/CreateView";

type InformatieObjectTypeTemplate = TemplateBase & {
  waarden: {
    catalogus: string;
    informatieobjectcategorie: string;
    vertrouwelijkheidaanduiding: string;
  };
};

export const INFORMATIEOBJECTTYPE_CREATE_BASE_FIELDS: FormField[] = [
  {
    label: "Omschrijving",
    name: "omschrijving",
    type: "text",
    required: true,
  },
];

export function InformatieObjectTypeCreatePage() {
  const obContext = useContext(OBContext);
  const params = useParams();
  const submitAction = useSubmitAction<InformatieObjectTypeCreateAction>(false);

  const catalogusUrl = obContext.catalogiChoices.find(
    (c) => getUUIDFromString(c.value) === params[CATALOGUS_PARAM],
  )?.value;

  const handleSubmit = (
    event: FormEvent<HTMLFormElement>,
    data: InformatieObjectTypeTemplate["waarden"],
  ) => {
    event.preventDefault();
    invariant(catalogusUrl, "catalogusUrl must be set!");

    const requestPayload = {
      beginGeldigheid: new Date().toISOString().substring(0, 10),
      ...data,
    } as InformatieObjectTypeCreateActionPayload;

    submitAction({
      type: "INFORMATIEOBJECTTYPE_CREATE",
      payload: requestPayload,
    });
  };

  const modalText =
    "Je staat op het punt een nieuw informatieobjecttype te starten. Vul deze velden in.";

  const templates: InformatieObjectTypeTemplate[] = [
    {
      uuid: "00000000-0000-0000-0000-000000000000",
      omschrijving: "Basis",
      voorbeelden: ["Zelf opbouwen", "Vertrouwelijkheidaanduiding: openbaar"],
      waarden: {
        catalogus: catalogusUrl || "",
        informatieobjectcategorie: "Een categorie",
        vertrouwelijkheidaanduiding: "openbaar",
      },
    },
  ];

  return (
    <CreateView<InformatieObjectTypeTemplate>
      formFields={INFORMATIEOBJECTTYPE_CREATE_BASE_FIELDS}
      modalText={modalText}
      resourceName="informatieobjecttype"
      templates={templates}
      onSubmit={handleSubmit}
    />
  );
}

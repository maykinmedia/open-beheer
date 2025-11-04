import {
  Body,
  Button,
  Card,
  CardBaseTemplate,
  Column,
  Form,
  FormField,
  FormValidator,
  Grid,
  H1,
  H2,
  Modal,
  Outline,
  P,
  Ul,
} from "@maykin-ui/admin-ui";
import { slugify, ucFirst } from "@maykin-ui/client-common";
import { invariant } from "@maykin-ui/client-common/assert";
import React, { FormEvent, useCallback } from "react";
import { useNavigation } from "react-router";
import { useBreadcrumbItems } from "~/hooks";

/**
 * Base shape of a template used to create a resource.
 */
export type TemplateBase = {
  uuid: string;
  naam?: string;
  omschrijving: string;
  voorbeelden?: string[];
  waarden: object;
};

/**
 * Props for CreateView. Used to generate a create flow based on a selected template.
 */
export type CreateViewProps<T extends TemplateBase> = {
  formFields: FormField[];
  modalText: string;
  nonFieldErrors?: string[];
  resourceName: string;
  templates: T[];
  onValidate?: FormValidator;
  onSubmit: (event: FormEvent<HTMLFormElement>, data: T["waarden"]) => void;
};

/**
 * Shows available templates and opens the create form modal when a template is chosen.
 */
export function CreateView<T extends TemplateBase = TemplateBase>({
  formFields,
  modalText,
  nonFieldErrors,
  resourceName,
  templates,
  onValidate,
  onSubmit,
}: CreateViewProps<T>) {
  const { state } = useNavigation();
  const breadcrumbItems = useBreadcrumbItems();

  const [isFillingForm, setIsFillingForm] = React.useState(false);
  const [valuesState, setValuesState] = React.useState<T | null>(null);

  const handleSelectTemplate = useCallback(
    (uuid: string) => {
      setValuesState(null);

      const selectedResult = templates.find((result) => result.uuid === uuid);
      if (selectedResult) {
        setValuesState({ ...selectedResult });
      }
    },
    [templates],
  );

  return (
    <CardBaseTemplate breadcrumbItems={breadcrumbItems}>
      <Modal
        size="m"
        title="Basis"
        open={isFillingForm}
        onClose={() => setIsFillingForm(false)}
      >
        <Body fullHeight>
          {Boolean(modalText) && <P>{modalText}</P>}
          <Form
            aria-label="Zaaktype aanmaken"
            nonFieldErrors={valuesState ? nonFieldErrors : undefined}
            fields={formFields}
            justify="stretch"
            buttonProps={{
              children: (
                <>
                  {ucFirst(resourceName)} aanmaken
                  {state !== "idle" && <Outline.ArrowPathIcon spin={true} />}
                </>
              ),
            }}
            validateOnChange
            showActions={true}
            validate={onValidate}
            onSubmit={(event, data) => {
              const values = valuesState?.waarden || {};
              if ("_expand" in values) delete values._expand;
              onSubmit(event, { ...values, ...data });
            }}
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
              Maak een nieuw {resourceName} aan door te starten vanaf een
              sjabloon.
            </P>
          </Column>
          <Column span={6} />

          {templates.map((template) => {
            invariant(typeof template.uuid, "template must have uuid set!");

            return (
              <Column
                span={3}
                key={template.uuid}
                className="createcard-wrapper"
              >
                <CreateCard<T>
                  template={template}
                  selectedTemplate={valuesState?.uuid || null}
                  setSelectedTemplate={handleSelectTemplate}
                />
              </Column>
            );
          })}
          <Column span={12}>
            <Button
              variant="primary"
              disabled={!valuesState?.uuid}
              onClick={() => setIsFillingForm(true)}
            >
              Gebruik dit sjabloon
            </Button>
          </Column>
        </Grid>
      </Body>
    </CardBaseTemplate>
  );
}

/**
 * Props for CreateCard.
 */
type CreateCardProps<T extends TemplateBase = TemplateBase> = {
  template: T;
  selectedTemplate: string | null;
  setSelectedTemplate: (uuid: string) => void;
};

/**
 * Card representing a single template option.
 */
export function CreateCard<T extends TemplateBase>({
  template,
  selectedTemplate,
  setSelectedTemplate,
}: CreateCardProps<T>) {
  invariant(template.uuid, "template must have uuid set!");
  const label = template.naam || template.omschrijving;

  return (
    <Card
      className="createcard"
      onClick={() => setSelectedTemplate(template.uuid)}
      border={true}
      titleAs={H2}
      title={label}
      actions={[
        {
          ["aria-label"]: label,
          type: "radio",
          name: `createcard-${slugify(label)}`,
          value: template.uuid,
          checked: selectedTemplate === template.uuid,
        },
      ]}
    >
      <Body fullHeight={true} className="createcard__body">
        <P>{template.omschrijving}</P>
        {Boolean(template.voorbeelden && template.voorbeelden.length > 0) && (
          <Ul>
            {template.voorbeelden?.map((voorbeeld: string) => (
              <li key={voorbeeld}>{voorbeeld}</li>
            ))}
          </Ul>
        )}
      </Body>
    </Card>
  );
}

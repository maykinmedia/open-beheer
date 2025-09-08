import type { Meta, StoryObj } from "@storybook/react";
import { HttpResponse, http } from "msw";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";
import { API_BASE_URL } from "~/api";
import {
  FIXTURE_CATALOGI_CHOICE,
  FIXTURE_CATALOGI_CHOICES,
  FIXTURE_SERVICE_CHOICE,
  FIXTURE_SERVICE_CHOICES,
  FIXTURE_TEMPLATES,
  FIXTURE_USER,
  FIXTURE_ZAAKTYPEN,
} from "~/fixtures";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { routes } from "~/routes.tsx";

import { ZaaktypeCreatePage as ZaaktypeCreatePageComponent } from "./";

const meta: Meta<typeof ZaaktypeCreatePageComponent> = {
  title: "Pages/ZaaktypeCreate",
  component: ZaaktypeCreatePageComponent,
  decorators: [withRouter],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const ZaaktypeCreatePage: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get(`${API_BASE_URL}/whoami/`, () =>
          HttpResponse.json(FIXTURE_USER),
        ),
        http.get(`${API_BASE_URL}/service/choices`, () =>
          HttpResponse.json(FIXTURE_SERVICE_CHOICES),
        ),
        http.get(
          `${API_BASE_URL}/service/${FIXTURE_SERVICE_CHOICE.value}/catalogi/choices`,
          () => HttpResponse.json(FIXTURE_CATALOGI_CHOICES),
        ),
        http.get(
          `${API_BASE_URL}/service/${FIXTURE_SERVICE_CHOICE.value}/zaaktypen`,
          () =>
            HttpResponse.json({
              results: FIXTURE_ZAAKTYPEN,
            }),
        ),
        http.get(`${API_BASE_URL}/template/zaaktype`, () =>
          HttpResponse.json({
            results: FIXTURE_TEMPLATES,
          }),
        ),
      ],
    },
    reactRouter: reactRouterParameters({
      location: {
        path: `/${FIXTURE_SERVICE_CHOICE.value}/$${getUUIDFromString(FIXTURE_CATALOGI_CHOICE.value)}/zaaktypen/create`,
      },
      routing: routes[0],
    }),
  },
};

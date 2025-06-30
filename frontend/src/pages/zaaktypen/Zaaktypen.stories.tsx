import type { Meta, StoryObj } from "@storybook/react";
import { DefaultBodyType, HttpResponse, PathParams, http } from "msw";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";
import { API_BASE_URL } from "~/api";
import { ListResponse } from "~/api/types";
import { FIXTURE_ZAAKTYPEN, FIXTURE_ZAAKTYPEN_FIELDS } from "~/fixtures";
import { routes } from "~/routes.tsx";
import { components } from "~/types";

import { ZaaktypenPage as ZaaktypenPageComponent } from "./Zaaktypen";

const meta: Meta<typeof ZaaktypenPageComponent> = {
  title: "Pages/Zaaktypen",
  component: ZaaktypenPageComponent,
  decorators: [withRouter],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const ZaaktypenPage: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<
          PathParams,
          DefaultBodyType,
          ListResponse<components["schemas"]["ZaakTypeSummary"]>
        >(`${API_BASE_URL}/service/open-zaak-catalogi-api/zaaktypen/`, () =>
          HttpResponse.json({
            fields: FIXTURE_ZAAKTYPEN_FIELDS,
            pagination: {
              count: 3,
              page: 1,
              pageSize: 100,
            },
            results: FIXTURE_ZAAKTYPEN,
          }),
        ),
      ],
    },
    reactRouter: reactRouterParameters({
      location: {
        path: `/open-zaak-catalogi-api/85028f4f-3d70-4ce9-8dbe-16a6b8613a54/zaaktypen/`,
      },
      routing: routes[0],
    }),
  },
};

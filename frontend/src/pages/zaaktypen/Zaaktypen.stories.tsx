import type { Meta, StoryObj } from "@storybook/react";
import { DefaultBodyType, HttpResponse, PathParams, http } from "msw";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";
import { API_BASE_URL } from "~/api";
import { ListResponse } from "~/api/types";
import { FIXTURE_ZAAKTYPEN, FIXTURE_ZAAKTYPE_FIELDS } from "~/fixtures";
import { routes } from "~/routes.tsx";
import { ZaakType } from "~/types";

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
        http.get<PathParams, DefaultBodyType, ListResponse<ZaakType>>(
          `${API_BASE_URL}/catalogi/zaaktypen`,
          () =>
            HttpResponse.json({
              fields: FIXTURE_ZAAKTYPE_FIELDS,
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
        path: "/catalogi/zaaktypen",
      },
      routing: routes[0],
    }),
  },
};

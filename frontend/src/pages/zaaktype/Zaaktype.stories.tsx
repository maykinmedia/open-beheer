import type { Meta, StoryObj } from "@storybook/react";
import { DefaultBodyType, HttpResponse, PathParams, http } from "msw";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";
import { API_BASE_URL } from "~/api";
import { DetailResponse, ListResponse } from "~/api/types";
import {
  FIXTURE_ZAAKTYPE,
  FIXTURE_ZAAKTYPEN,
  FIXTURE_ZAAKTYPE_FIELDS,
} from "~/fixtures";
import { routes } from "~/routes.tsx";
import { ZaakType } from "~/types";

import { ZaaktypePage as ZaaktypePageComponent } from "./Zaaktype";

const meta: Meta<typeof ZaaktypePageComponent> = {
  title: "Pages/Zaaktype",
  component: ZaaktypePageComponent,
  decorators: [withRouter],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const ZaaktypePage: Story = {
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
        http.get<PathParams, DefaultBodyType, DetailResponse<ZaakType>>(
          `${API_BASE_URL}/catalogi/zaaktypen/${FIXTURE_ZAAKTYPE.uuid}`,
          () =>
            HttpResponse.json({
              fields: FIXTURE_ZAAKTYPE_FIELDS,
              result: FIXTURE_ZAAKTYPE,
            }),
        ),
      ],
    },
    reactRouter: reactRouterParameters({
      location: {
        path: `/catalogi/zaaktypen/${FIXTURE_ZAAKTYPE.uuid}`,
      },
      routing: routes[0],
    }),
  },
};

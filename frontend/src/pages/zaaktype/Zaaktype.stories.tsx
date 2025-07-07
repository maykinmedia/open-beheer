import type { Meta, StoryObj } from "@storybook/react";
import { DefaultBodyType, HttpResponse, PathParams, http } from "msw";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";
import { API_BASE_URL } from "~/api";
import {
  FIXTURE_ZAAKTYPE,
  FIXTURE_ZAAKTYPE_FIELDS,
  FIXTURE_ZAAKTYPE_FIELDSETS,
} from "~/fixtures";
import { routes } from "~/routes.tsx";
import { components } from "~/types";

import { ZaaktypePage as ZaaktypePageComponent } from "./Zaaktype";

const meta: Meta<typeof ZaaktypePageComponent> = {
  title: "Pages/Zaaktype",
  component: ZaaktypePageComponent,
  decorators: [withRouter],
};

export default meta;
type Story = StoryObj<typeof meta>;

const zaaktypeUUID = FIXTURE_ZAAKTYPE.url.split("/").pop();

export const ZaaktypePage: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<
          PathParams,
          DefaultBodyType,
          components["schemas"]["DetailResponse_ZaakType_"]
        >(
          `${API_BASE_URL}/service/open-zaak-catalogi-api/zaaktypen/${zaaktypeUUID}`,
          () =>
            HttpResponse.json({
              fields: FIXTURE_ZAAKTYPE_FIELDS,
              fieldsets: FIXTURE_ZAAKTYPE_FIELDSETS,
              result: FIXTURE_ZAAKTYPE,
            } as components["schemas"]["DetailResponse_ZaakType_"]),
        ),
      ],
    },
    reactRouter: reactRouterParameters({
      location: {
        path: `/open-zaak-catalogi-api/85028f4f-3d70-4ce9-8dbe-16a6b8613a54/zaaktypen/${zaaktypeUUID}`,
      },
      routing: routes[0],
    }),
  },
};

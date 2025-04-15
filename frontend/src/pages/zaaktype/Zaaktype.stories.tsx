import type { Meta, StoryObj } from "@storybook/react";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";

import { ZaaktypePage as ZaaktypePageComponent } from "./Zaaktype";
import { zaaktypeLoader } from "./zaaktype.loader";

const meta: Meta<typeof ZaaktypePageComponent> = {
  title: "Pages/Zaaktype",
  component: ZaaktypePageComponent,
  decorators: [withRouter],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const ZaaktypePage: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { id: "42" },
      },
      routing: {
        path: ":id",
        loader: zaaktypeLoader,
      },
    }),
  },
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
  },
};

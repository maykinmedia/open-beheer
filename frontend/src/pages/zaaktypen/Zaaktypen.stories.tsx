import type { Meta, StoryObj } from "@storybook/react";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";
import { zaaktypenLoader } from "~/pages";

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
    reactRouter: reactRouterParameters({
      routing: {
        loader: zaaktypenLoader,
      },
    }),
  },
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
  },
};

import type { Meta, StoryObj } from "@storybook/react";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";

import { CatalogiPage as CatalogiPageComponent } from "./Catalogi";
import { catalogiLoader } from "./catalogi.loader";

const meta: Meta<typeof CatalogiPageComponent> = {
  title: "Pages/Catalogi",
  component: CatalogiPageComponent,
  decorators: [withRouter],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const CatalogiPage: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      routing: {
        loader: catalogiLoader,
      },
    }),
  },
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
  },
};

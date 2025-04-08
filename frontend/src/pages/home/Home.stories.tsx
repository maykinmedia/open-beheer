import type { Meta, StoryObj } from "@storybook/react";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";

import { HomePage as HomePageComponent } from "./Home";
import { HomeLoaderData } from "./Home.loader.tsx";

const meta: Meta<typeof HomePageComponent> = {
  title: "Pages/Home",
  component: HomePageComponent,
  decorators: [withRouter],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const HomePage: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      routing: {
        loader: () => ({}) as HomeLoaderData,
      },
    }),
  },
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
  },
};

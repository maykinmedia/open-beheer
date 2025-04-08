import type { Meta, StoryObj } from "@storybook/react";

import { HomePage as HomePageComponent } from "./Home";

const meta: Meta<typeof HomePageComponent> = {
  title: "Pages/Home",
  component: HomePageComponent,
};

export default meta;
type Story = StoryObj<typeof meta>;

export const HomePage: Story = {
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
  },
};

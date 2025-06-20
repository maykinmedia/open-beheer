import type { Meta, StoryObj } from "@storybook/react";

import { ZaaktypeFilter as ZaaktypeFilterComponent } from "./ZaaktypeFilter";

const meta: Meta<typeof ZaaktypeFilterComponent> = {
  title: "Components/ZaaktypeFilter",
  component: ZaaktypeFilterComponent,
  argTypes: {
    onSubmit: { action: "onSubmit" },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const ZaaktypeFilter: Story = {
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
  },
};

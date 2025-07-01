import { action } from "@storybook/addon-actions";
import type { Meta, StoryObj } from "@storybook/react";
import { userEvent, within } from "@storybook/test";

import { VersionSelector as VersionSelectorComponent } from "./VersionSelector.tsx";

const meta: Meta<typeof VersionSelectorComponent> = {
  title: "Components/VersionSelector",
  component: VersionSelectorComponent,
};

export default meta;
type Story = StoryObj<typeof meta>;

export const VersionSelector: Story = {
  args: {
    versions: [
      {
        uuid: "v1",
        concept: false,
        beginGeldigheid: "2024-01-01",
        eindeGeldigheid: "2025-12-31",
      },
      {
        uuid: "v0",
        concept: false,
        beginGeldigheid: "2022-01-01",
        eindeGeldigheid: "2023-12-31",
      },
      {
        uuid: "v2",
        concept: false,
        beginGeldigheid: "2026-01-01",
        eindeGeldigheid: null,
      },
      {
        uuid: "v2-draft",
        concept: true,
        beginGeldigheid: "2025-08-01",
        eindeGeldigheid: null,
      },
    ],
    onVersionChange: action("onVersionChange"),
  },
  play: async ({ canvasElement }) => {
    const fixedNow = new Date("2025-07-01").valueOf();
    const originalDateNow = Date.now;
    Date.now = () => fixedNow; // Mocking the currentt date

    const canvas = within(canvasElement);

    const expandButton = await canvas.findByRole("button", {
      name: /toon meer/i,
    });
    await userEvent.click(expandButton);

    const historicalBtn = await canvas.findByRole("button", {
      name: /selecteer historische versie v0/i,
    });
    await userEvent.click(historicalBtn);

    Date.now = originalDateNow;
  },
};

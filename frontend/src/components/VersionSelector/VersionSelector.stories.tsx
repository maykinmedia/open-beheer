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
        uuid: "v0",
        concept: false,
        beginGeldigheid: "2022-01-01",
        eindeGeldigheid: "2022-12-31",
      },
      {
        uuid: "v0.1",
        concept: false,
        beginGeldigheid: "2023-01-01",
        eindeGeldigheid: "2023-12-31",
      },
      {
        uuid: "v0.2",
        concept: false,
        beginGeldigheid: "2024-01-01",
        eindeGeldigheid: "2024-12-31",
      },
      {
        uuid: "v1",
        concept: false,
        beginGeldigheid: "2025-01-01",
        eindeGeldigheid: "2025-12-31",
      },
      {
        uuid: "v2",
        concept: true,
        beginGeldigheid: "2025-08-01",
        eindeGeldigheid: null,
      },
    ],
    onVersionChange: action("onVersionChange"),
  },
  play: async ({ canvasElement }) => {
    const fixedNow = new Date("2025-07-01").valueOf();
    Date.now = () => fixedNow;

    const canvas = within(canvasElement);

    const expandButton = await canvas.findByRole("button", {
      name: /toon meer/i,
    });
    await userEvent.click(expandButton);

    const selecteerButtons = await canvas.findAllByRole("button", {
      name: /selecteer/i,
    });
    await userEvent.click(selecteerButtons[4]);
    await userEvent.click(selecteerButtons[3]);
    await userEvent.click(selecteerButtons[2]);
    await userEvent.click(selecteerButtons[1]);
    await userEvent.click(selecteerButtons[0]);

    await userEvent.click(expandButton);

    // Check if button 0 is still selected
    const actueelButton = await canvas.findByRole("button", {
      name: /actueel/i,
    });
    await userEvent.click(actueelButton);
  },
};

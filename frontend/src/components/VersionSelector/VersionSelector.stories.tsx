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
    currentVersionUUID: "37454e74-99cd-4689-9589-c819ad8f1b88",
    versions: [
      {
        uuid: "09d7c3b6-153e-4bcf-b8cd-55c11ffd2c76",
        concept: false,
        beginGeldigheid: "2022-01-01",
        eindeGeldigheid: "2022-12-31",
      },
      {
        uuid: "08370480-e843-4d9c-aced-56ddb8595d22",
        concept: false,
        beginGeldigheid: "2023-01-01",
        eindeGeldigheid: "2023-12-31",
      },
      {
        uuid: "0dd7a5ca-9c49-4750-a063-616ed00040e6",
        concept: false,
        beginGeldigheid: "2024-01-01",
        eindeGeldigheid: "2024-12-31",
      },
      {
        uuid: "fc685de7-d386-4d9f-861c-244700d68e80",
        concept: false,
        beginGeldigheid: "2025-01-01",
        eindeGeldigheid: "2025-12-31",
      },
      {
        uuid: "37454e74-99cd-4689-9589-c819ad8f1b88",
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

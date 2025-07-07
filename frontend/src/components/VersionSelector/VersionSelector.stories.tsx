import { action } from "@storybook/addon-actions";
import type { Meta, StoryObj } from "@storybook/react";
import { userEvent, within } from "@storybook/test";
import { FIXTURE_ZAAKTYPE_VERSIONS } from "~/fixtures";

import { VersionSelector as VersionSelectorComponent } from "./VersionSelector.tsx";

const meta: Meta<typeof VersionSelectorComponent> = {
  title: "Components/VersionSelector",
  component: VersionSelectorComponent,
};

export default meta;
type Story = StoryObj<typeof meta>;

export const VersionSelector: Story = {
  args: {
    selectedVersionUUID: FIXTURE_ZAAKTYPE_VERSIONS[4]["uuid"],
    versions: FIXTURE_ZAAKTYPE_VERSIONS,
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

export const NoCurrentVersion: Story = {
  args: {
    versions: FIXTURE_ZAAKTYPE_VERSIONS.filter((v) => v.concept),
    onVersionChange: action("onVersionChange"),
  },
};

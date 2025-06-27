import type { Meta, StoryObj } from "@storybook/react";

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
        uuid: "1",
        begin_geldigheid: "2023-01-01",
        einde_geldigheid: null,
        concept: false,
      },
      {
        uuid: "2",
        begin_geldigheid: "2024-01-01",
        einde_geldigheid: "2023-12-31",
        concept: false,
      },
      {
        uuid: "3",
        begin_geldigheid: "2024-02-01",
        einde_geldigheid: null,
        concept: true,
      },
      {
        uuid: "4",
        begin_geldigheid: "2024-03-01",
        einde_geldigheid: null,
        concept: false,
      },
    ],
    onVersionChange: (versionId: string) => {
      console.log("Selected version:", versionId);
    },
  },
};

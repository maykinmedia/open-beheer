import { P } from "@maykin-ui/admin-ui";
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
      { label: "Version 142", id: "142" },
      { label: "Current Version 143", id: "143", isCurrent: true },
      { label: "Concept Version 144", id: "144", isConcept: true },
      { label: "Version 145", id: "145" },
      { label: "Version 146", id: "146" },
    ],
    content: [
      {
        id: "142",
        children: <P>Content for Version 1</P>,
      },
      {
        id: "143",
        children: <P>Content for Version 2</P>,
      },
      {
        id: "144",
        children: <P>Content for Version 3 (Concept)</P>,
      },
      {
        id: "145",
        children: <P>Content for Version 4</P>,
      },
      {
        id: "146",
        children: <P>Content for Version 5</P>,
      },
    ],
  },
};

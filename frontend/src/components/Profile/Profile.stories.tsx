import type { Meta, StoryObj } from "@storybook/react";

import { Profile as ProfileComponent } from "./Profile";

const meta: Meta<typeof ProfileComponent> = {
  title: "Components/Profile",
  component: ProfileComponent,
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Profile: Story = {
  args: {
    user: {
      pk: 1,
      username: "johndoe",
      firstName: "John",
      lastName: "Doe",
      email: "johndoe@gmail.com",
    },
  },
};

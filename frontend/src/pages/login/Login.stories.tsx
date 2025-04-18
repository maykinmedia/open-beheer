import type { Meta, StoryObj } from "@storybook/react";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";
import { loginLoader } from "~/pages";

import { LoginPage as LoginPageComponent } from "./Login";

const meta: Meta<typeof LoginPageComponent> = {
  title: "Pages/Login",
  component: LoginPageComponent,
  decorators: [withRouter],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const LoginPage: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      routing: {
        loader: loginLoader,
      },
    }),
  },
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
  },
};

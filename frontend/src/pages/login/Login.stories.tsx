import type { Meta, StoryObj } from "@storybook/react";
import { DefaultBodyType, HttpResponse, PathParams, http } from "msw";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";
import { API_BASE_URL } from "~/api";
import { FIXTURE_USER } from "~/fixtures";
import { routes } from "~/routes.tsx";
import { User } from "~/types";

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
    msw: {
      handlers: [
        http.get<PathParams, DefaultBodyType, User>(
          `${API_BASE_URL}/whoami/`,
          () => HttpResponse.json(FIXTURE_USER),
        ),
      ],
    },
    reactRouter: reactRouterParameters({
      location: {
        path: "/login",
      },
      routing: routes[0],
    }),
  },
};

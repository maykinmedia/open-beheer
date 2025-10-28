import type { Meta, StoryObj } from "@storybook/react";
import { expect, within } from "@storybook/test";
import { DefaultBodyType, HttpResponse, PathParams, http } from "msw";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";
import { API_BASE_URL, OidcInfoType } from "~/api";
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
        http.get<PathParams, DefaultBodyType, OidcInfoType>(
          `${API_BASE_URL}/oidc-info/`,
          () => HttpResponse.json({ enabled: false }),
        ),
        http.get<PathParams, DefaultBodyType, undefined>(
          `${API_BASE_URL}/auth/ensure-csrf-token/`,
          () => new HttpResponse<undefined>(undefined, { status: 204 }),
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

export const LoginPageWithOIDC: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<PathParams, DefaultBodyType, User>(
          `${API_BASE_URL}/whoami/`,
          () => HttpResponse.json(FIXTURE_USER),
        ),
        http.get<PathParams, DefaultBodyType, OidcInfoType>(
          `${API_BASE_URL}/oidc-info/`,
          () =>
            HttpResponse.json({
              enabled: true,
              loginUrl: "http://backend.nl/oidc/authenticate",
            }),
        ),
        http.get<PathParams, DefaultBodyType, undefined>(
          `${API_BASE_URL}/auth/ensure-csrf-token/`,
          () => new HttpResponse<undefined>(undefined, { status: 204 }),
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
  play: async (context) => {
    const canvas = within(context.canvasElement);
    const oidcButton: HTMLBaseElement = await canvas.findByRole("link", {
      name: "Organisatie login",
    });
    const redirectUrl = new URL(oidcButton.href);
    const nextUrl = redirectUrl.searchParams.get("next");
    expect(nextUrl).not.toBeNull();
    expect(new URL(nextUrl as string).pathname).toEqual("/");
  },
};

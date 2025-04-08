import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  addons: [
    "@storybook/addon-essentials",
    "@storybook/addon-onboarding",
    "@chromatic-com/storybook",
    "@storybook/experimental-addon-test",
    "storybook-addon-remix-react-router",
    {
      name: "@storybook/addon-coverage",
      options: {
        istanbul: {
          exclude: ["**/*.stories.*", "**/.storybook/**", "**/fixtures/**"],
        },
      },
    },
  ],
  core: {
    disableTelemetry: true,
  },
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
};
export default config;

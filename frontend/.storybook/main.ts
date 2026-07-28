import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  addons: [
    "@chromatic-com/storybook",
    "@storybook/addon-vitest",
    "storybook-addon-remix-react-router",
    {
      name: "@storybook/addon-coverage",
      options: {
        istanbul: {
          exclude: ["**/*.stories.*", "**/.storybook/**", "**/fixtures/**"],
        },
      },
    },
    "@storybook/addon-docs",
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

import { defineConfig } from "vitest/config";

import config from "./vite.config";

export default defineConfig({
  ...config,
  test: {
    globals: true,
    environment: "jsdom",
    css: true,
    reporters: ["verbose"],
    coverage: {
      provider: "istanbul",
      reporter: ["text", "json", "html"],
      include: ["src/**/*"],
      exclude: ["**/*.stories.tsx"],
    },
  },
});

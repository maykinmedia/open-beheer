import { ignoreBuildArtifacts } from "@maykinmedia/eslint-config";
import maykin from "@maykinmedia/eslint-config/recommended";
import storybook from "eslint-plugin-storybook";
import eslint_plugin_tsdoc from "eslint-plugin-tsdoc";

const config = [
  ignoreBuildArtifacts(["build", "storybook-static"]),
  {
    ignores: ["bin", "coverage", "dist"],
  },
  ...storybook.configs["flat/recommended"],
  ...maykin,
  {
    plugins: {
      tsdoc: eslint_plugin_tsdoc,
    },
    rules: {
      "tsdoc/syntax": "error",
    },
  },
];

export default config;

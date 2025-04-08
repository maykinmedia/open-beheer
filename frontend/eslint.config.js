import { ignoreBuildArtifacts } from "@maykinmedia/eslint-config";
import recommended from "@maykinmedia/eslint-config/recommended";
import eslint_plugin_tsdoc from "eslint-plugin-tsdoc";

const config = [
  ignoreBuildArtifacts(["build", "storybook-static"]),
  ...recommended,
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

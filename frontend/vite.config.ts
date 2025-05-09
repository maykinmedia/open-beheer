import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    assetsDir: "static/assets",
  },
  envPrefix: "MYKN_",
  optimizeDeps: {
    include: ["react", "react-dom", "react-dom/client"],
  },
  resolve: {
    alias: {
      "~": path.resolve(__dirname, "src"),
    },
  },
});

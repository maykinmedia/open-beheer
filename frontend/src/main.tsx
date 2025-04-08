import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router";

import { HomePage } from "./pages";

const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
  },
]);

const root = document.getElementById("root") as HTMLElement;

createRoot(root).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);

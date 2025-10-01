import { ModalService } from "@maykin-ui/admin-ui";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router";
import { routes } from "~/routes.tsx";

import "./main.css";

const router = createBrowserRouter(routes);

const root = document.getElementById("root") as HTMLElement;

createRoot(root).render(
  <StrictMode>
    <ModalService>
      <RouterProvider router={router} />
    </ModalService>
  </StrictMode>,
);

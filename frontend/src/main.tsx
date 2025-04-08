import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router";
import App from "~/App.tsx";
import { homeAction } from "~/pages/home/Home.action.tsx";
import { homeLoader } from "~/pages/home/Home.loader.tsx";
import { loginAction } from "~/pages/login/Login.action.tsx";
import { loginLoader } from "~/pages/login/Login.loader.tsx";

import "./main.css";
import { HomePage, LoginPage } from "./pages";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "/",
        element: <HomePage />,
        loader: homeLoader,
        action: homeAction,
      },
      {
        path: "/login",
        element: <LoginPage />,
        loader: loginLoader,
        action: loginAction,
      },
    ],
  },
]);

const root = document.getElementById("root") as HTMLElement;

createRoot(root).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
